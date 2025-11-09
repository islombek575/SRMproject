import io

import openpyxl
from apps.forms import ProductForm
from apps.mixins import RoleRequiredMixin
from apps.models import Product
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Q, Sum
from django.http import FileResponse, HttpResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


class ProductListView(RoleRequiredMixin, ListView):
    allowed_roles = ['admin']
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):

        self.query = self.request.GET.get('q', '')
        self.category_id = self.request.GET.get('category', '')

        queryset = super().get_queryset().order_by('-id')

        if self.query:
            queryset = queryset.filter(
                Q(name__icontains=self.query) | Q(barcode__icontains=self.query)
            )

        if self.category_id:
            queryset = queryset.filter(category_id=self.category_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total_products = self.model.objects.count()

        total_stock_value = self.model.objects.aggregate(
            total=Sum(F('cost_price') * F('stock'))
        )['total'] or 0
        low_stock_count = self.model.objects.filter(stock__lte=5).count()

        context['query'] = self.query
        context['selected_category'] = self.category_id
        context['total_products'] = total_products
        context['total_stock_value'] = total_stock_value
        context['low_stock_count'] = low_stock_count

        return context


class ProductCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    allowed_roles = ['admin']
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Yangi mahsulot qo'shish"
        return context


class ProductUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    allowed_roles = ['admin']
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('product_list')
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Mahsulotni tahrirlash"
        return context


class ProductDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    allowed_roles = ['admin']
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')
    context_object_name = 'product'
    pk_url_kwarg = 'pk'


class ExportProductsPDFView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = ['admin']

    def get(self, request, *args, **kwargs):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        p.setFont("Helvetica-Bold", 16)
        p.drawString(200, height - 50, "📦 Ombordagi mahsulotlar")

        p.setFont("Helvetica-Bold", 12)
        y = height - 100
        p.drawString(50, y, "Nomi")
        p.drawString(200, y, "Barcode")
        p.drawString(300, y, "Kategoriya")
        p.drawString(400, y, "Narxi")
        p.drawString(480, y, "Soni")

        y -= 20
        p.setFont("Helvetica", 10)
        products = Product.objects.all()
        for prod in products:
            p.drawString(50, y, prod.name)
            p.drawString(200, y, prod.barcode or "-")
            p.drawString(400, y, str(prod.sell_price))
            p.drawString(480, y, str(prod.stock))
            y -= 20
            if y < 50:
                p.showPage()
                y = height - 50

        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename="products.pdf")


class ExportProductsExcelView(RoleRequiredMixin, View):
    allowed_roles = ['admin']

    def get(self, request, *args, **kwargs):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Products"

        headers = ["Nomi", "Barcode", "Kategoriya", "Sotib olish narxi", "Sotish narxi", "Soni"]
        ws.append(headers)

        for p in Product.objects.all():
            ws.append([
                p.name,
                p.barcode or "-",
                float(p.cost_price),
                float(p.sell_price),
                p.stock
            ])

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename=products.xlsx'
        wb.save(response)
        return response
