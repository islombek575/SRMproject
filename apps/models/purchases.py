from decimal import Decimal

from django.db import transaction

from apps.models import Product
from apps.models.base import UUIDBaseModel
from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    DecimalField,
    ForeignKey,
    Model,
    TextChoices,
)

from apps.utils import to_decimal


class Purchase(UUIDBaseModel):
    class StatusChoices(TextChoices):
        PENDING = "PENDING", "Pending"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    status = CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    total_price = DecimalField(max_digits=12, decimal_places=2)
    purchased_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Purchase #{self.id}"

    def recalc_total(self):
        total = sum((item.total_price for item in self.items.all()), Decimal('0.00'))
        self.total_price = to_decimal(total)
        return self.total_price

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.recalc_total()
        super().save(update_fields=['total_price'])


class PurchaseItem(Model):
    purchase = ForeignKey(Purchase, on_delete=CASCADE, related_name="items")
    product = ForeignKey(Product, on_delete=CASCADE)
    quantity = DecimalField(max_digits=10, decimal_places=2)
    cost_price = DecimalField(max_digits=12, decimal_places=2)

    @property
    def total_price(self):
        return to_decimal(self.quantity) * to_decimal(self.cost_price)


    def save(self, *args, **kwargs):
        is_new = self.pk is None
        with transaction.atomic():
            super().save(*args, **kwargs)
            self.purchase.recalc_total()
            self.purchase.save(update_fields=['total_price'])
            if is_new:
                self.product.increase_stock(self.quantity)

    def __str__(self):
        return f"{self.product.name} x {self.quantity} {self.product.unit}"

