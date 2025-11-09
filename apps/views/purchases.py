from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.views import View
from weasyprint import HTML

from apps.mixins import RoleRequiredMixin
from apps.models import Purchase, PurchaseItem, Product


class PurchaseListView(RoleRequiredMixin, View):
    allowed_roles = ['admin']

    def get(self, request):
        selected_date = request.GET.get('date')
        purchases = Purchase.objects.all().order_by('-purchased_at')

        if selected_date:
            purchases = purchases.filter(purchased_at__date=selected_date)

        total_sales = purchases.aggregate(total=Sum('total_price'))['total'] or 0

        return render(request, 'purchases/purchase_list.html', {
            'purchases': purchases,
            'total_sales': total_sales,
            'selected_date': selected_date,
        })


class PurchaseDetailView(RoleRequiredMixin, View):
    allowed_roles = ['admin']

    def get(self, request, pk):
        purchase = get_object_or_404(Purchase, id=pk)
        return render(request, 'purchases/purchase_detail.html', {'purchase': purchase})


class AddPurchaseView(RoleRequiredMixin, View):
    allowed_roles = ['admin']

    def get(self, request):
        products = Product.objects.all()
        return render(request, 'purchases/add_purchase.html', {'products': products})

    def post(self, request):
        products = Product.objects.all()
        product_ids = request.POST.getlist('product')
        quantities = request.POST.getlist('quantity')

        if not product_ids or not quantities:
            messages.error(request, "Mahsulot tanlanmagan.")
            return redirect('add_purchase')

        purchase = Purchase.objects.create(total_price=0, status="PENDING")
        total_price = 0

        for product_id, quantity in zip(product_ids, quantities):
            product = Product.objects.get(id=product_id)
            qty = int(quantity)

            item_total = product.cost_price * qty
            total_price += item_total

            PurchaseItem.objects.create(
                purchase=purchase,
                product=product,
                quantity=qty,
                cost_price=product.cost_price
            )

        purchase.total_price = total_price
        purchase.save()

        messages.success(request, "Purchase qo'shildi ✅")
        return redirect('purchase_list')


class PurchasePDFView(RoleRequiredMixin, View):
    allowed_roles = ['admin']

    def get(self, request, pk):
        purchase = get_object_or_404(Purchase, id=pk)
        html_string = render_to_string('purchases/purchase_pdf.html', {'purchase': purchase})
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'filename="purchase_{purchase.id}.pdf"'
        HTML(string=html_string).write_pdf(response)
        return response


class PurchaseCompleteView(RoleRequiredMixin, View):
    allowed_roles = ['admin']

    def post(self, request, pk):
        purchase = get_object_or_404(Purchase, pk=pk)

        if purchase.status == "PENDING":
            items = PurchaseItem.objects.filter(purchase=purchase)
            total_price = 0

            for item in items:
                product = item.product
                product.stock += item.quantity
                product.save()

                total_price += item.cost_price * item.quantity

            purchase.total_price = total_price
            purchase.status = "COMPLETED"
            purchase.save()

            messages.success(request, "Purchase yakunlandi ✅")
        else:
            messages.warning(request, "Faqat PENDING purchase yakunlanishi mumkin.")

        return redirect("purchase_list")


class PurchaseCancelView(RoleRequiredMixin, View):
    allowed_roles = ['admin']

    def post(self, request, pk):
        purchase = get_object_or_404(Purchase, pk=pk)

        if purchase.status == "PENDING":
            purchase.status = "CANCELLED"
            purchase.save()
            messages.success(request, "Purchase bekor qilindi ❌")
        else:
            messages.warning(request, "Bu purchase allaqachon bekor qilingan.")

        return redirect("purchase_list")
