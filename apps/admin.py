from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name','total_debt')
    search_fields = ('name',)

from django.contrib import admin
from apps.models.products import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','barcode','sell_price','stock','created_at')
    search_fields = ('name','barcode')

from django.contrib import admin
from apps.models import Sale, SaleItem

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    inlines = [SaleItemInline]
    list_display = ('id','customer','cashier','payment_type','total_amount','created_at')
    list_filter = ('payment_type','created_at')

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from apps.models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Role', {'fields':('role',)}),
    )
    list_display = ('username','email','first_name','last_name','role','is_staff')


