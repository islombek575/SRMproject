from apps.mixins import RoleRequiredMixin
from apps.models import Product, Purchase, PurchaseItem
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views import View
from django.views.generic import DetailView, ListView
from weasyprint import HTML


class PurchaseListView(RoleRequiredMixin, ListView):
    allowed_roles = ['admin']
    model = Purchase
    template_name = 'purchases/purchase_list.html'
    context_object_name = 'purchases'
    paginate_by = 5

    def get_queryset(self):
        selected_date = self.request.GET.get('date')
        queryset = super().get_queryset().order_by('-purchased_at')

        if selected_date:
            queryset = queryset.filter(purchased_at__date=selected_date)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        queryset = self.get_queryset()
        total_sales = queryset.aggregate(total=Sum('total_price'))['total'] or 0

        context['total_sales'] = total_sales
        context['selected_date'] = self.request.GET.get('date')
        return context


class PurchaseDetailView(RoleRequiredMixin, DetailView):
    allowed_roles = ['admin']
    model = Purchase
    template_name = 'purchases/purchase_detail.html'
    context_object_name = 'purchase'
    pk_url_kwarg = 'pk'


class AddPurchaseView(RoleRequiredMixin, View):
    allowed_roles = ['admin']

    def get(self, request):
        products = Product.objects.all()
        return render(request, 'purchases/add_purchase.html', {'products': products})

    def post(self, request):
        product_ids = request.POST.getlist('product')
        quantities = request.POST.getlist('quantity')

        if not product_ids or not quantities:
            messages.error(request, "Mahsulot tanlanmagan.")
            return redirect('add_purchase')

        try:
            purchase = Purchase.objects.create(total_price=0, status="PENDING")
            total_price = 0

            for product_id, quantity in zip(product_ids, quantities):

                if product_id and int(quantity) > 0:
                    product = get_object_or_404(Product, id=product_id)
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

        except Exception as e:
            messages.error(request, f"Xatolik yuz berdi: {e}")
            return redirect('add_purchase')


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
