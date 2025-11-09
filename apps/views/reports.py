import json
from datetime import date, timedelta

from apps.mixins import RoleRequiredMixin
from apps.models import Purchase, Sale, SaleItem
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import DecimalField, F, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.views import View


class ReportsView(RoleRequiredMixin, LoginRequiredMixin, View):
    allowed_roles = ['admin']
    template_name = "reports/dashboard.html"

    def _get_dates(self, request):
        today = date.today()
        start_date_str = request.GET.get("start_date")
        end_date_str = request.GET.get("end_date")

        start_date = date.fromisoformat(start_date_str) if start_date_str else today - timedelta(days=6)
        end_date = date.fromisoformat(end_date_str) if end_date_str else today

        return today, start_date, end_date

    def get(self, request):
        today, start_date, end_date = self._get_dates(request)

        sales_range = Sale.objects.filter(created_at__date__range=[start_date, end_date])
        purchases_range = Purchase.objects.filter(purchased_at__date__range=[start_date, end_date])

        sales_today = Sale.objects.filter(created_at__date=today)
        purchases_today = Purchase.objects.filter(purchased_at__date=today)

        revenue_agg = sales_range.aggregate(total=Sum("total_amount"))
        total_revenue = revenue_agg["total"] or 0

        cogs_agg = SaleItem.objects.filter(sale__in=sales_range).aggregate(
            cost=Sum(F("quantity") * F("product__cost_price"), output_field=DecimalField())
        )
        total_cost = cogs_agg["cost"] or 0

        total_profit = total_revenue - total_cost

        expenses_agg = purchases_range.aggregate(exp=Sum("total_price"))
        total_expenses = expenses_agg["exp"] or 0

        net_profit = total_profit - total_expenses

        today_metrics = self._calculate_daily_metrics(sales_today, purchases_today)

        top_products = self._get_top_products(sales_range)
        payment_stats = self._get_payment_stats(sales_range)
        cashier_stats = self._get_cashier_stats(sales_range)
        daily_stats = self._get_daily_trend(sales_range)

        context = {

            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),

            "total_revenue": total_revenue,
            "total_profit": total_profit,
            "total_expenses": total_expenses,
            "net_profit": net_profit,

            "today_revenue": today_metrics['revenue'],
            "today_profit": today_metrics['profit'],
            "today_expenses": today_metrics['expenses'],
            "today_net": today_metrics['net'],

            "top_products": json.dumps(list(top_products), cls=DjangoJSONEncoder),
            "payment_stats": json.dumps(list(payment_stats), cls=DjangoJSONEncoder),
            "cashier_stats": json.dumps(list(cashier_stats), cls=DjangoJSONEncoder),
            "daily_stats": json.dumps(daily_stats, cls=DjangoJSONEncoder),
        }

        return render(request, self.template_name, context)

    def _calculate_daily_metrics(self, sales, purchases):
        revenue = sales.aggregate(total=Sum("total_amount"))["total"] or 0

        cogs_agg = SaleItem.objects.filter(sale__in=sales).aggregate(
            cost=Sum(F("quantity") * F("product__cost_price"), output_field=DecimalField())
        )
        cost = cogs_agg["cost"] or 0

        profit = revenue - cost

        expenses = purchases.aggregate(exp=Sum("total_price"))["exp"] or 0
        net = profit - expenses

        return {'revenue': revenue, 'profit': profit, 'expenses': expenses, 'net': net}

    def _get_top_products(self, sales):
        return (
            SaleItem.objects.filter(sale__in=sales)
            .values("product__name")
            .annotate(qty=Sum("quantity"))
            .order_by("-qty")[:5]
        )

    def _get_payment_stats(self, sales):
        return (
            sales.values("payment_type")
            .annotate(total=Sum("total_amount"))
        )

    def _get_cashier_stats(self, sales):
        return (
            sales.values("cashier__username")
            .annotate(total=Sum("total_amount"))
        )

    def _get_daily_trend(self, sales):
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

        results = []
        for d in daily_stats:
            profit = d["revenue"] - (d["cost"] or 0)
            results.append({
                "day": d["day"].strftime("%Y-%m-%d"),
                "revenue": float(d["revenue"] or 0),
                "profit": float(profit or 0),
            })

        return results
