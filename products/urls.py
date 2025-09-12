from django.urls import path
from products.views import (
    DashboardView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    ProductDetailView,
)

app_name = "products"

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('product/create/', ProductCreateView.as_view(), name='product_create'),
    path('product/<uuid:pk>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('product/<uuid:uuid>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('product/<uuid:uuid>/', ProductDetailView.as_view(), name='product_detail'),
]
