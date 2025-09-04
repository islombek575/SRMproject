from django.contrib import admin
from .models import Customer, Sale, SaleItem
from reports.models import Report


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")



class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "total_amount", "created_at")
    list_filter = ("created_at",)
    search_fields = ("customer__name",)
    date_hierarchy = "created_at"
    inlines = [SaleItemInline]


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ("id", "sale", "product_name", "quantity", "price", "subtotal")
    search_fields = ("product_name",)
    list_filter = ("sale__created_at",)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "total_sales", "total_transactions")
