from django.contrib.auth.decorators import login_required
from django.urls import path

from .views import (
    DashboardView, ProductCreateView,
    ProductUpdateView, ProductDeleteView, admin_panel
)

urlpatterns = [
    path('', login_required(DashboardView.as_view(), login_url='user_login'), name="dashboard_view"),
    path('create/', ProductCreateView.as_view(), name="product_create_view"),
    path('<uuid:pk>/update/', ProductUpdateView.as_view(), name="product_update_view"),
    path('<uuid:pk>/delete/', ProductDeleteView.as_view(), name="product_delete_view"),
    path('admin-panel/', admin_panel, name='admin_panel'),
]
