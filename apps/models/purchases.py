import uuid
from decimal import Decimal

from apps.models import Product
from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    DecimalField,
    ForeignKey,
    Model,
    PositiveIntegerField,
    TextChoices,
    UUIDField,
)


class Purchase(Model):
    class StatusChoices(TextChoices):
        PENDING = "PENDING", "Pending"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    id = UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    status = CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    total_price = DecimalField(max_digits=12, decimal_places=2)
    purchased_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Purchase #{self.id}"


class PurchaseItem(Model):
    purchase = ForeignKey(Purchase, on_delete=CASCADE, related_name="items")
    product = ForeignKey(Product, on_delete=CASCADE)
    quantity = DecimalField(max_digits=10, decimal_places=2)
    cost_price = DecimalField(max_digits=12, decimal_places=2)

    @property
    def total_price(self):
        return (self.quantity * self.cost_price).quantize(Decimal("0.01"))

    def save(self, *args, **kwargs):
        if not self.pk:
            self.product.increase_stock(self.quantity)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x {self.quantity} {self.product.unit}"


