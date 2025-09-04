from django.contrib import admin
from inventory.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "stock", "created_at")
    search_fields = ("name", "id")
    list_filter = ("created_at",)
    ordering = ("-created_at",)
