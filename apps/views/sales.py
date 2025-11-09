import json
import os
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import DetailView
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from apps.mixins import RoleRequiredMixin
from apps.models import Debt
from apps.models import Sale, SaleItem, Customer, Product


class GetProductView(RoleRequiredMixin, LoginRequiredMixin, View):
    allowed_roles = ['admin', 'cashier']

    def get(self, request):
        barcode = request.GET.get("barcode")
        try:
            product = Product.objects.get(barcode=barcode)
            return JsonResponse({
                "success": True,
                "barcode": product.barcode,
                "name": product.name,
                "price": float(product.sell_price),
                "stock": product.stock,
            })
        except Product.DoesNotExist:
            return JsonResponse({"success": False, "message": "❌ Mahsulot topilmadi!"})


class SaleCreateView(RoleRequiredMixin, LoginRequiredMixin, View):
    allowed_roles = ['admin', 'cashier']

    @transaction.atomic
    def post(self, request):
        try:
            # === POST ma’lumotlarni olish ===
            total_amount = Decimal(request.POST.get('total_amount', 0))
            payment_type = request.POST.get('payment_type')
            received_amount = Decimal(request.POST.get('received_amount', 0))
            customer_name = request.POST.get('customer_name', '').strip()
            cart_data = request.POST.get('cart_data')

            # === Savatchani tekshirish ===
            if not cart_data:
                messages.error(request, "Savatcha bo‘sh.")
                return redirect("pos_page")

            cart_items = json.loads(cart_data)
            if not cart_items:
                messages.error(request, "Savatchada mahsulot yo‘q.")
                return redirect("pos_page")

            # === Savdo summasini tekshirish ===
            if total_amount <= 0:
                messages.error(request, "❌ Savdo summasi 0 bo‘lishi mumkin emas!")
                return self._redirect_by_role(request)

            # === Nasiya uchun mijoz ===
            customer = None
            if payment_type == "credit":
                if len(customer_name) < 3:
                    messages.error(request, "Nasiya uchun mijoz ismini kiriting.")
                    return self._redirect_by_role(request)
                customer, _ = Customer.objects.get_or_create(name=customer_name)

            # === Savdoni yaratish ===
            sale = Sale.objects.create(
                customer=customer,
                cashier=request.user if request.user.is_authenticated else None,
                payment_type=payment_type,
                total_amount=total_amount,
                paid_amount=received_amount,
            )

            # === Har bir mahsulotni yozish ===
            for item in cart_items:
                barcode = item.get("barcode")
                qty = Decimal(item.get("qty", 1))
                price = Decimal(item.get("price", 0))

                product = Product.objects.filter(barcode=barcode).first()
                if not product:
                    messages.warning(request, f"{item.get('name')} topilmadi.")
                    continue

                if product.stock < qty:
                    messages.error(request, f"{product.name} uchun yetarli mahsulot yo‘q!")
                    raise Exception("Stock yetarli emas")

                # SaleItem yozish
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=qty,
                    price=price,
                )

                # Ombordagi miqdorni kamaytirish
                product.stock -= qty
                product.save()

            # === To‘lovni tekshirish ===
            if payment_type in ["cash", "card"]:
                if received_amount < total_amount:
                    messages.error(request, "❌ To‘lov summasi umumiy summadan kam bo‘lishi mumkin emas!")
                    raise Exception("To‘lov summasi kam")

            # === Nasiya holati ===
            if payment_type == "credit" and sale.customer:
                debt_amount = total_amount - received_amount
                if debt_amount > 0:
                    sale.customer.total_debt += debt_amount
                    sale.customer.save()

                    # Debt yozamiz
                    Debt.objects.create(
                        customer=sale.customer,
                        amount=total_amount,
                        paid_amount=received_amount,
                        created_by=request.user,
                    ).update_status()

            messages.success(request, "✅ Savdo muvaffaqiyatli amalga oshirildi!")
            return redirect("dashboard")

        except Exception as e:
            transaction.set_rollback(True)
            messages.error(request, f"❌ Xatolik yuz berdi: {str(e)}")
            return self._redirect_by_role(request)

    # === GET (sahifani ochish) ===
    def get(self, request):
        template = "sales/add_sale.html" if request.user.role == "admin" else "sales/add_sale_for_employees.html"
        return render(request, template)

    # === Role bo‘yicha qaytarish helper ===
    def _redirect_by_role(self, request):
        if request.user.role == "admin":
            return redirect("sale_create")
        return render(request, "sales/add_sale_for_employees.html")


class SaleHistoryView(RoleRequiredMixin, LoginRequiredMixin, View):
    allowed_roles = ['admin']

    def get(self, request):
        filter_date = request.GET.get("date")
        if filter_date:
            sales_list = Sale.objects.filter(created_at__date=filter_date).order_by("-created_at")
        else:
            sales_list = Sale.objects.all().order_by("-created_at")

        paginator = Paginator(sales_list, 10)
        page_number = request.GET.get("page")
        sales = paginator.get_page(page_number)

        return render(request, "sales/sale_history.html", {"sales": sales})


class SaleDetailView(LoginRequiredMixin, DetailView):
    queryset = Sale.objects.all()
    template_name = 'sales/sale_detail.html'
    context_object_name = 'sale'


# class SaleDetailView(LoginRequiredMixin, View):
#
#     def get(self, request, pk):
#         sale = get_object_or_404(Sale, pk=pk)
#         return render(request, "sales/sale_detail.html", {"sale": sale})


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

        logo_path = os.path.join('/home/islombek/PycharmProjects/SRMproject/static/logo.png')
        if os.path.exists(logo_path):
            logo = ImageReader(logo_path)
            p.drawImage(logo, width / 2 - 15 * mm, y - 20 * mm, width=30 * mm, height=20 * mm, preserveAspectRatio=True,
                        mask='auto')
        y -= 25 * mm

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

        if sale.PAYMENT.CASH:
            p.drawString(2 * mm, y, f"Berilgan summa: {sale.paid_amount}")
            y -= 5 * mm
            p.drawString(2 * mm, y, f"Qaytim: {sale.total_amount-sale.paid_amount}")
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
            subtotal = f"{int(item.subtotal()):,}"

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
