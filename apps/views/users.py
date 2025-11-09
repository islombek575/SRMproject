from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views import View
from django.db.models import Sum
from datetime import timedelta
import json

from apps.forms import CustomPasswordChangeForm
from apps.mixins import RoleRequiredMixin
from apps.models import Product
from apps.models import User, Sale

class CustomLoginView(LoginView):
    template_name = "users/login.html"


    redirect_authenticated_user = True
    allowed_roles = ["admin", "cashier"]


class CustomLogoutView(LogoutView):
    next_page = 'login'
    allowed_roles = ["admin", "cashier"]


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = "users/change_password.html"
    success_url = reverse_lazy("profile")


class ProfileView(RoleRequiredMixin, View):
    allowed_roles = ["admin", "cashier"]


    def get(self, request, *args, **kwargs):
        if request.user.role == 'admin':
            return render(request, 'users/profile.html', {'user': request.user})
        return render(request, 'users/employees_profile.html', {'user': request.user})


class DashboardView(RoleRequiredMixin, View):
    allowed_roles = ["admin", "cashier"]


    def get(self, request, *args, **kwargs):
        if request.user.role == 'admin':
            today = timezone.now().date()
            total_sales_today = Sale.objects.filter(created_at__date=today).count()
            total_amount_today = float(Sale.objects.filter(created_at__date=today)
                                       .aggregate(total=Sum('total_amount'))['total'] or 0)
            total_products = Product.objects.count()
            total_employees = User.objects.filter(is_staff=True).count()
            recent_sales = Sale.objects.order_by('-created_at')[:5]

            last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
            sales_chart_labels = [d.strftime("%d-%m") for d in last_7_days]
            sales_chart_data = [
                float(Sale.objects.filter(created_at__date=d)
                      .aggregate(total=Sum('total_amount'))['total'] or 0)
                for d in last_7_days
            ]

            context = {
                'total_sales_today': total_sales_today,
                'total_amount_today': total_amount_today,
                'total_products': total_products,
                'total_employees': total_employees,
                'recent_sales': recent_sales,
                'sales_chart_labels': json.dumps(sales_chart_labels),
                'sales_chart_data': json.dumps(sales_chart_data),
            }
            return render(request, 'dashboard.html', context)

        return redirect("sale_create")
