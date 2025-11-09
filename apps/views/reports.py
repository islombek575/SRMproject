from datetime import timedelta, date
import json
from django.views import View
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import TruncDate
from django.shortcuts import render

from apps.models import Purchase, Sale, SaleItem
from apps.mixins import RoleRequiredMixin

class ReportsView(RoleRequiredMixin, LoginRequiredMixin, View):
    allowed_roles = ['admin']


    def get(self, request):
        today = date.today()
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        if not start_date:
            start_date = today - timedelta(days=6)
        else:
            start_date = date.fromisoformat(start_date)
        if not end_date:
            end_date = today
        else:
            end_date = date.fromisoformat(end_date)

        # Savdolar va xarajatlar
        sales = Sale.objects.filter(created_at__date__range=[start_date, end_date])
        purchases = Purchase.objects.filter(purchased_at__date__range=[start_date, end_date])

        # KPI’lar
        total_revenue = sales.aggregate(total=Sum("total_amount"))["total"] or 0
        total_cost = (
                SaleItem.objects.filter(sale__in=sales)
                .aggregate(cost=Sum(F("quantity") * F("product__cost_price"),
                                    output_field=DecimalField()))["cost"] or 0
        )
        total_profit = total_revenue - total_cost
        total_expenses = purchases.aggregate(exp=Sum("total_price"))["exp"] or 0
        net_profit = total_profit - total_expenses

        # Bugungi ko‘rsatkichlar
        today_sales = Sale.objects.filter(created_at__date=today)
        today_revenue = today_sales.aggregate(total=Sum("total_amount"))["total"] or 0
        today_cost = (
                SaleItem.objects.filter(sale__in=today_sales)
                .aggregate(cost=Sum(F("quantity") * F("product__cost_price"),
                                    output_field=DecimalField()))["cost"] or 0
        )
        today_profit = today_revenue - today_cost
        today_expenses = Purchase.objects.filter(purchased_at__date=today).aggregate(exp=Sum("total_price"))["exp"] or 0
        today_net = today_profit - today_expenses

        # Top 5 mahsulotlar
        top_products = (
            SaleItem.objects.filter(sale__in=sales)
            .values("product__name")
            .annotate(qty=Sum("quantity"))
            .order_by("-qty")[:5]
        )

        # To‘lov statistikasi
        payment_stats = (
            sales.values("payment_type")
            .annotate(total=Sum("total_amount"))
        )

        # Kassir statistikasi
        cashier_stats = (
            sales.values("cashier__username")
            .annotate(total=Sum("total_amount"))
        )

        # Kunlik trend
        daily_stats = (
            sales.annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(
                revenue=Sum("total_amount"),
                cost=Sum(F("items__quantity") * F("items__product__cost_price"),
                         output_field=DecimalField())
            )
            .order_by("day")
        )
        for d in daily_stats:
            d["profit"] = d["revenue"] - (d["cost"] or 0)

        context = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "total_revenue": total_revenue,
            "total_profit": total_profit,
            "total_expenses": total_expenses,
            "net_profit": net_profit,

            "today_revenue": today_revenue,
            "today_profit": today_profit,
            "today_expenses": today_expenses,
            "today_net": today_net,

            "top_products": json.dumps(list(top_products), cls=DjangoJSONEncoder),
            "payment_stats": json.dumps(list(payment_stats), cls=DjangoJSONEncoder),
            "cashier_stats": json.dumps(list(cashier_stats), cls=DjangoJSONEncoder),
            "daily_stats": json.dumps(
                [
                    {
                        "day": d["day"].strftime("%Y-%m-%d"),
                        "revenue": float(d["revenue"] or 0),
                        "profit": float(d["profit"] or 0),
                    }
                    for d in daily_stats
                ],
                cls=DjangoJSONEncoder
            ),
        }

        return render(request, "reports/dashboard.html", context)

