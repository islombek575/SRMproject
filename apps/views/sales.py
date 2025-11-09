import json
from decimal import Decimal as Dec

from apps.mixins import RoleRequiredMixin
from apps.models import Customer, Debt, Product, Sale, SaleItem
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView, ListView, CreateView
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


class GetProductView(RoleRequiredMixin, LoginRequiredMixin, View):
    allowed_roles = ['admin', 'cashier']

    def get(self, request):
        barcode = request.GET.get("barcode")
        try:
            product = Product.objects.get(Q(barcode=barcode))
            return JsonResponse({
                "success": True,
                "barcode": product.barcode,
                "name": product.name,
                "price": float(product.sell_price),
                "stock": product.stock,
                "unit": product.unit,
            })
        except Product.DoesNotExist:
            return JsonResponse({"success": False, "message": "❌ Mahsulot topilmadi!"})


class SaleCreateView(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    allowed_roles = ['admin', 'cashier']
    success_url = 'dashboard'

    def _redirect_by_role(self, request):
        if request.user.role == "admin":
            return redirect("sale_create")
        template = "sales/add_sale_for_employees.html"
        return render(request, template)

    def get(self, request):
        template = "sales/add_sale.html" if request.user.role == "admin" else "sales/add_sale_for_employees.html"
        return render(request, template)

    @transaction.atomic
    def post(self, request):

        try:

            total_amount = Dec(request.POST.get('total_amount', 0) or 0)

            payment_type = request.POST.get('payment_type')
            received_amount = Dec(request.POST.get('received_amount', 0) or 0)

            customer_name = request.POST.get('customer_name', '').strip()
            cart_data = request.POST.get('cart_data')

            cart_items = json.loads(cart_data)

            if total_amount <= 0 or not cart_items:
                messages.error(request, "❌ Savdo summasi 0 bo‘lishi yoki savatcha bo‘sh bo‘lishi mumkin emas!")
                return self._redirect_by_role(request)

            customer = None
            if payment_type == "credit":
                if len(customer_name) < 3:
                    messages.error(request, "Nasiya uchun mijoz ismini kiriting.")
                    return self._redirect_by_role(request)
                customer, _ = Customer.objects.get_or_create(name=customer_name)

            sale = Sale.objects.create(
                customer=customer,
                cashier=request.user,
                payment_type=payment_type,
                total_amount=total_amount,
                paid_amount=received_amount,
            )

            for item in cart_items:
                barcode = item.get("barcode")
                qty = Dec(item.get("qty", 1) or 1)
                price = Dec(item.get("price", 0) or 0)

                product = Product.objects.filter(Q(barcode=barcode)).first()

                if not product:
                    messages.warning(request, f"{item.get('name')} topilmadi.")
                    continue

                if product.stock < qty:
                    messages.error(request, f"{product.name} uchun yetarli mahsulot yo‘q!")
                    raise ValueError(f"Stock yetarli emas: {product.name}")

                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=qty,
                    price=price,
                )

                product.stock -= qty

                product.save()

            debt_amount = total_amount - received_amount

            if payment_type in ["cash", "card"] and received_amount < total_amount:
                messages.error(request, "❌ To‘lov summasi umumiy summadan kam bo‘lishi mumkin emas!")
                raise ValueError("To‘lov summasi kam")

            if payment_type == "credit" and debt_amount > 0 and sale.customer:
                sale.customer.total_debt += debt_amount
                sale.customer.save()

                debt = Debt.objects.create(
                    customer=sale.customer,
                    amount=total_amount,
                    paid_amount=received_amount,
                    created_by=request.user,
                )

                debt.update_status()

            messages.success(request, "✅ Savdo muvaffaqiyatli amalga oshirildi!")
            return JsonResponse({"success": True, "sale_id": sale.id})

        except ValueError as e:
            transaction.set_rollback(True)
            return JsonResponse({"success": False, "message": str(e)})

        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({"success": False, "message": "Kutilmagan xatolik: " + str(e)})


class SaleHistoryView(RoleRequiredMixin, LoginRequiredMixin, ListView):
    allowed_roles = ['admin']
    model = Sale
    template_name = "sales/sale_history.html"
    context_object_name = 'sales'
    paginate_by = 10

    def get_queryset(self):
        filter_date = self.request.GET.get("date")
        queryset = super().get_queryset().order_by("-created_at")

        if filter_date:
            queryset = queryset.filter(created_at__date=filter_date)

        return queryset


class SaleDetailView(LoginRequiredMixin, DetailView):
    queryset = Sale.objects.all()
    template_name = 'sales/sale_detail.html'
    context_object_name = 'sale'
    pk_url_kwarg = 'pk'


class SaleReceiptPDFView(RoleRequiredMixin, LoginRequiredMixin, View):
    allowed_roles = ['admin']

    def get(self, request, sale_id):
        sale = get_object_or_404(Sale, pk=sale_id)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="receipt_{sale.id}.pdf"'

        page_width = 80 * mm
        page_height = A4[1]
        p = canvas.Canvas(response, pagesize=(page_width, page_height))
        width, height = page_width, page_height
        y = height - 10 * mm

        p.setFont("Courier", 7)

        p.drawCentredString(width / 2, y, "🏪 DILYORBEK MARKET")
        y -= 3 * mm
        p.drawCentredString(width / 2, y, "📍 Farg'ona vil., Quva tumani")
        y -= 3 * mm
        p.drawCentredString(width / 2, y, "☎ +998 90 123 45 67")
        y -= 5 * mm

        p.drawString(2 * mm, y, f"Sana: {sale.created_at.strftime('%Y-%m-%d %H:%M')}")
        y -= 3 * mm
        p.drawString(2 * mm, y, f"Kassir: {sale.cashier.username if sale.cashier else '-'}")
        y -= 3 * mm
        p.drawString(2 * mm, y, f"To‘lov: {sale.get_payment_type_display()}")
        y -= 5 * mm

        if sale.payment_type in ['cash', 'card']:
            p.drawString(2 * mm, y, f"Berilgan summa: {sale.paid_amount}")
            y -= 5 * mm
            p.drawString(2 * mm, y, f"Qaytim: {sale.paid_amount - sale.total_amount}")
            y -= 5 * mm

        p.drawString(2 * mm, y, "-" * 39)
        y -= 3 * mm
        p.drawString(2 * mm, y, "Mahsulot       | Soni | Narx    | Jami")
        y -= 2 * mm
        p.drawString(2 * mm, y, "-" * 39)
        y -= 3 * mm

        for item in sale.items.all():
            name = item.product.name
            qty = str(item.quantity)
            price = f"{int(item.price):,}"
            subtotal = f"{int(item.subtotal):,}"

            max_len = 14
            name_lines = [name[i:i + max_len] for i in range(0, len(name), max_len)]

            for i, line_name in enumerate(name_lines):
                if i == 0:
                    line = f"{line_name:<14} | {qty:>3}  | {price:>7} | {subtotal:>7}"
                else:
                    line = f"{line_name:<14} |      |         |       "
                p.drawString(2 * mm, y, line)
                y -= 3 * mm

            p.drawString(2 * mm, y, "-" * 39)
            y -= 3 * mm

            if y < 20 * mm:
                p.showPage()
                p.setFont("Courier", 7)
                y = height - 10 * mm

        p.drawString(2 * mm, y, "=" * 39)
        y -= 5 * mm
        p.drawRightString(width - 2 * mm, y, f"Jami: {int(sale.total_amount):,} so‘m")
        y -= 7 * mm

        p.drawCentredString(width / 2, y, "✅ Rahmat! Sizni kutib qolamiz!")
        y -= 5 * mm

        p.showPage()
        p.save()
        return response
