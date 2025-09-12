import uuid
from decimal import Decimal

from django.db import models
from django.db.models import Sum, F
from django.db.models.fields import DateTimeField

from customers.models import Customer
from products.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()

class Sale(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("finished", "Finished"),
        ("cancelled", "Cancelled"),
    ]

    TYPE_CHOICES = [
        ("cash", "Cash"),
        ("cart", "Cart"),
        ("credit", "Credit"),
    ]


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, editable=False)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    change_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    payment_type = models.CharField(max_length=10,choices=TYPE_CHOICES, default="cash")
    created_at = DateTimeField(auto_now_add=True)

    def calculate_total(self):
        total = self.items.aggregate(total=Sum(F("price") * F("quantity")))["total"] or 0
        self.total_amount = total
        self.change_amount = self.paid_amount - total if self.paid_amount > 0 else 0
        self.save(update_fields=["total_amount", "change_amount"])

    def __str__(self):
        return f"Sale #{self.id} - {self.get_status_display()}"


class SaleItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale = models.ForeignKey(Sale, related_name="items", on_delete=models.CASCADE)
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, editable=False)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # quantity ni int ga o‘tkazamiz
        qty = int(self.quantity) if self.quantity else 0
        # subtotal hisoblash
        self.subtotal = (self.price or Decimal("0")) * Decimal(qty)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
