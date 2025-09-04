from django.contrib.auth.decorators import login_required
from django.urls import path

from .views import (
    DashboardView, admin_panel, UserCreateView, export_sales_excel, export_sales_pdf
)

urlpatterns = [
    path('', login_required(DashboardView.as_view(), login_url='user_login'), name="dashboard_view"),
    path('admin-panel/', admin_panel, name='admin_panel'),
    path('users/create/', UserCreateView.as_view(), name='user_create_view'),
    path('export/sales/excel/', export_sales_excel, name='export_sales_excel'),
    path('export/sales/pdf/', export_sales_pdf, name='export_sales_pdf'),

]
