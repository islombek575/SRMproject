from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from root.settings import MEDIA_URL, MEDIA_ROOT, STATIC_URL, STATIC_ROOT

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls', namespace='users')),
    ]  + static(MEDIA_URL, document_root=MEDIA_ROOT) + static(STATIC_URL, document_root=STATIC_ROOT)

"""
    path('', include("inventory.urls", namespace='inventory')),
    path('products/', include('products.urls', namespace='products')),
    path('sales/', include('sales.urls', namespace='sales')),
    path('reports/', include('reports.urls', namespace='reports')),
    path("credits/", include("credits.urls", namespace="credits")),
"""