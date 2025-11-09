import io

import openpyxl
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import FileResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from apps.forms import ProductForm
from apps.mixins import RoleRequiredMixin
from apps.models import Product


class ProductListView(RoleRequiredMixin, View):
    allowed_roles = ['admin']

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        category_id = request.GET.get('category', '')

        products = Product.objects.order_by('-id')
        if query:
            products = products.filter(name__icontains=query) | products.filter(barcode__icontains=query)
        if category_id:
            products = products.filter(category_id=category_id)

        paginator = Paginator(products, 10)
        page_number = request.GET.get('page')
        products_page = paginator.get_page(page_number)

        total_products = Product.objects.count()
        total_stock_value = sum(p.cost_price * p.stock for p in Product.objects.all())
        low_stock_count = Product.objects.filter(stock__lte=5).count()

        context = {
            'products': products_page,
            'query': query,
            'selected_category': category_id,
            'total_products': total_products,
            'total_stock_value': total_stock_value,
            'low_stock_count': low_stock_count,
        }
        return render(request, 'products/product_list.html', context)


class ProductCreateView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = ['admin']

    def get(self, request, *args, **kwargs):
        form = ProductForm()
        return render(request, 'products/product_form.html', {'form': form, 'title': "Yangi mahsulot qo'shish"})

    def post(self, request, *args, **kwargs):
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
        return render(request, 'products/product_form.html', {'form': form, 'title': "Yangi mahsulot qo'shish"})


class ProductUpdateView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = ['admin']

    def get(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, pk=pk)
        form = ProductForm(instance=product)
        return render(request, 'products/product_form.html', {'form': form, 'title': "Mahsulotni tahrirlash"})

    def post(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, pk=pk)
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
        return render(request, 'products/product_form.html', {'form': form, 'title': "Mahsulotni tahrirlash"})


class ProductDeleteView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = ['admin']

    def get(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, pk=pk)
        return render(request, 'products/product_confirm_delete.html', {'product': product})

    def post(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return redirect('product_list')


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
                p.barcode,
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
