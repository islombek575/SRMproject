import json
from datetime import timedelta

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, F
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic import ListView

from sales.models import Sale, SaleItem
from .forms import ProductForm
from .models import Product


class DashboardView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "inventory/dashboard.html"
    context_object_name = "products"
    queryset = Product.objects.order_by("-created_at")
    login_url = "user_login"
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = timezone.localdate()

        # Bugungi va umumiy savdo
        context["today_sales"] = Sale.objects.filter(created_at__date=today).aggregate(
            total=Sum("total_amount")
        )["total"] or 0

        context["total_sales"] = Sale.objects.aggregate(total=Sum("total_amount"))["total"] or 0

        # Top 5 mahsulot
        context["top_products"] = (
            SaleItem.objects.values(product_title=F("product_name"))
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

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = "inventory/product_form.html"
    success_url = reverse_lazy("product_list")


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "inventory/product_form.html"
    success_url = reverse_lazy("product_list")


class ProductDeleteView(DeleteView):
    model = Product
    template_name = "inventory/product_confirm_delete.html"
    success_url = reverse_lazy("product_list")
