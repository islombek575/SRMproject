import io
import json
from datetime import timedelta

import xlsxwriter
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, F
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import ListView
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from credits.models import Credit
from products.models import Product
from sales.models import Sale, SaleItem


class DashboardView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "inventory/dashboard.html"
    context_object_name = "products"
    queryset = Product.objects.order_by("-created_at")
    login_url = "users:user_login"
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = timezone.localdate()

        # Bugungi va umumiy savdo
        context["today_sales"] = Sale.objects.filter(created_at__date=today).aggregate(
            total=Sum("total_amount")
        )["total"] or 0

        context["total_sales"] = Sale.objects.aggregate(total=Sum("total_amount"))["total"] or 0

        context["total_credits"] = Credit.objects.aggregate(total=Sum("amount"))["total"] or 0

        # Top 5 mahsulot
        context["top_products"] = (
            SaleItem.objects.values(product_title=F("product"))
            .annotate(quantity_sold=Sum("quantity"), total_sales=Sum("subtotal"))
            .order_by("-quantity_sold")[:5]
        )

        # Oxirgi 5 ta savdo
        context["recent_sales"] = Sale.objects.select_related("customer").order_by("-created_at")[:5]

        # Oxirgi 7 kunlik savdo statistikasi
        last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
        context["sales_labels"] = json.dumps([day.strftime("%d-%m") for day in last_7_days])
        context["sales_data"] = json.dumps([
            float(Sale.objects.filter(created_at__date=day).aggregate(total=Sum("total_amount"))["total"] or 0)
            for day in last_7_days
        ])

        # Foydalanuvchi rollari
        user = self.request.user
        context["is_superuser"] = user.is_superuser
        context["is_cashier"] = user.groups.filter(name='cashier').exists() and not user.is_superuser

        return context


@user_passes_test(lambda u: u.is_superuser)
def admin_panel(request):
    today_sales = Sale.objects.filter(created_at__date=timezone.localdate()).aggregate(total=Sum("total_amount"))["total"] or 0
    total_sales = Sale.objects.aggregate(total=Sum("total_amount"))["total"] or 0
    products_count = Product.objects.count()
    recent_sales = Sale.objects.select_related("customer").order_by("-created_at")[:5]

    context = {
        "today_sales": today_sales,
        "total_sales": total_sales,
        "products_count": products_count,
        "recent_sales": recent_sales,
    }
    return render(request, "users/admin-panel.html", context)



# views.py
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import get_user_model
from inventory.forms import UserForm

User = get_user_model()


class UserCreateView(UserPassesTestMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = "users/user-form.html"
    success_url = reverse_lazy("admin_panel")

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        form.save_m2m()
        return super().form_valid(form)


def export_sales_excel(request):
    if not request.user.is_superuser:
        return HttpResponse("Ruxsat yo'q", status=403)

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet("Sales")

    headers = ['Mijoz', 'Summasi', 'Sana']
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header)

    sales = Sale.objects.select_related('customer').all().order_by('-created_at')
    for row_num, sale in enumerate(sales, start=1):
        worksheet.write(row_num, 0, sale.customer.name if sale.customer else "Umumiy mijoz")
        worksheet.write(row_num, 1, sale.total_amount)
        worksheet.write(row_num, 2, sale.created_at.strftime("%d-%m-%Y %H:%M"))

    workbook.close()
    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = 'attachment; filename=sales.xlsx'
    return response


# PDF export
def export_sales_pdf(request):
    if not request.user.is_superuser:
        return HttpResponse("Ruxsat yo'q", status=403)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Oxirgi Savdo Hisoboti")
    y -= 40
    p.setFont("Helvetica", 12)
    sales = Sale.objects.select_related('customer').all().order_by('-created_at')
    for sale in sales:
        text = f"{sale.created_at.strftime('%d-%m-%Y %H:%M')} | {sale.customer.name if sale.customer else 'Umumiy mijoz'} | {sale.total_amount} so'm"
        p.drawString(50, y, text)
        y -= 20
        if y < 50:
            p.showPage()
            y = height - 50
    p.showPage()
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

