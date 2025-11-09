import uuid

from apps.models import Product
from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    DecimalField,
    ForeignKey,
    Model,
    PositiveIntegerField,
    UUIDField,
)


class Purchase(Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]
    id = UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    status = CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    total_price = DecimalField(max_digits=12, decimal_places=2)
    purchased_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Purchase #{self.id}"


class PurchaseItem(Model):
    purchase = ForeignKey(Purchase, on_delete=CASCADE, related_name="items")
    product = ForeignKey(Product, on_delete=CASCADE)
    quantity = PositiveIntegerField()
    cost_price = DecimalField(max_digits=12, decimal_places=2)

    @property
    def total_price(self):
        return self.quantity * self.cost_price

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
