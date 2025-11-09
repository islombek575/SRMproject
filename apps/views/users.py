import json
from datetime import timedelta

from apps.forms import CustomPasswordChangeForm
from apps.mixins import RoleRequiredMixin
from apps.models import Product, Sale, User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View


class CustomLoginView(LoginView):
    template_name = "users/login.html"
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = "users/change_password.html"
    success_url = reverse_lazy("profile")


class ProfileView(RoleRequiredMixin, LoginRequiredMixin, View):
    allowed_roles = ["admin", "cashier"]

    def get(self, request, *args, **kwargs):
        if request.user.role == 'admin':
            template = 'users/profile.html'
        else:
            template = 'users/employees_profile.html'

        return render(request, template, {'user': request.user})


class DashboardView(RoleRequiredMixin, LoginRequiredMixin, View):
    allowed_roles = ["admin", "cashier"]

    def get(self, request, *args, **kwargs):

        if request.user.role != 'admin':
            return redirect("sale_create")

        today = timezone.now().date()

        today_sales_queryset = Sale.objects.filter(created_at__date=today)
        total_sales_today = today_sales_queryset.count()
        total_amount_today = float(today_sales_queryset
                                   .aggregate(total=Sum('total_amount'))['total'] or 0)

        total_products = Product.objects.count()
        total_employees = User.objects.filter(is_staff=True).count()
        recent_sales = Sale.objects.order_by('-created_at')[:5]

        last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
        sales_chart_labels = [d.strftime("%d-%m") for d in last_7_days]

        sales_chart_data = []
        for d in last_7_days:
            amount = Sale.objects.filter(created_at__date=d) \
                         .aggregate(total=Sum('total_amount'))['total'] or 0
            sales_chart_data.append(float(amount))

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
