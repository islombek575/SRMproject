from django.db.models import Sum
from django.views import View

from products.models import Product


def dashboard_view(request):
    today = now().date()
    seven_days_ago = today - timedelta(days=6)  # oxirgi 7 kun

    # Umumiy statistikalar
    total_products = Product.objects.count()
    total_value = Product.objects.aggregate(total=Sum('price')*Sum('stock'))['total'] or 0
    total_sales = Sale.objects.count()
    total_revenue = Sale.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    today_revenue = Sale.objects.filter(created_at=today).aggregate(total=Sum('total_amount'))['total'] or 0

    # Eng ko'p sotilgan mahsulotlar
    top_products = (
        Sale.objects.values('items__product__name')
        .annotate(quantity_sold=Sum('items__quantity'))
        .order_by('-quantity_sold')[:5]
    ) 

    # 7 kunlik tushum
    last7_days = []
    last7_days_labels = []
    for i in range(7):
        day = seven_days_ago + timedelta(days=i)
        day_total = Sale.objects.filter(created_at=day).aggregate(total=Sum('total_amount'))['total'] or 0
        last7_days.append(day_total)
        last7_days_labels.append(day.strftime('%d-%m'))

    # Kategoriya bo'yicha sotuvlar
    category_data = (
        Sale.objects.values('items__product__category__name')
        .annotate(total=Sum('total_amount'))
    )
    category_names = [c['items__product__category__name'] for c in category_data]
    category_totals = [c['total'] for c in category_data]

    # Tugab borayotgan mahsulotlar
    low_stock = Product.objects.filter(stock__lte=5)

    context = {
        'total_products': total_products,
        'total_value': total_value,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'today_revenue': today_revenue,
        'top_products': top_products,
        'last7_days_labels': last7_days_labels,
        'last7_days_revenue': last7_days,
        'category_names': category_names,
        'category_totals': category_totals,
        'low_stock': low_stock,
    }

    return render(request, 'reports/dashboard.html', context)


# reports/views.py (yoki sales/views.py)
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.timezone import now
import csv

from sales.models import Sale



@login_required
def sales_history(request):
    today = now().date()
    start = request.GET.get("start")
    end = request.GET.get("end")
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")

    qs = Sale.objects.select_related("customer", "seller").prefetch_related("items__product").order_by("-created_at")

    # default — oxirgi 30 kun
    if not start and not end:
        start_date = today - timedelta(days=30)
        end_date = today
        qs = qs.filter(created_at__date__range=(start_date, end_date))
    else:
        if start:
            qs = qs.filter(created_at__date__gte=start)
        if end:
            qs = qs.filter(created_at__date__lte=end)

    if q:
        qs = qs.filter(customer__name__icontains=q) | qs.filter(id__icontains=q)

    if status:
        qs = qs.filter(status=status)

    # export CSV
    if request.GET.get("export") == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=sales_history.csv"
        writer = csv.writer(response)
        writer.writerow(["sale_id", "date", "customer", "seller", "total_amount", "paid_amount", "status", "items"])
        for s in qs:
            items_str = "; ".join([f"{it.product.name} x{it.quantity}" for it in s.items.all()])
            writer.writerow([str(s.id), s.created_at.isoformat(), s.customer.name if s.customer else "", s.seller.username if s.seller else "", f"{s.total_amount:.2f}", f"{s.paid_amount:.2f}", s.status, items_str])
        return response

    paginator = Paginator(qs, 20)
    page = request.GET.get("page")
    sales = paginator.get_page(page)

    return render(request, "reports/history.html", {"sales": sales, "q": q, "start": start, "end": end, "status": status})
