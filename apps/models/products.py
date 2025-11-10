from decimal import Decimal

from django.db import transaction

from apps.models.base import CreatedBaseModel, UUIDBaseModel
from django.db.models import CharField, DecimalField, TextChoices

from apps.utils import to_decimal, CENTS


class Product(CreatedBaseModel, UUIDBaseModel):
    class UnitChoices(TextChoices):
        piece = "piece", "Dona"
        kg = "kg", "Kilogram"

    name = CharField(max_length=255)
    barcode = CharField(max_length=50, unique=True)
    cost_price = DecimalField(max_digits=12, decimal_places=2)
    sell_price = DecimalField(max_digits=12, decimal_places=2)
    unit = CharField(max_length=10, choices=UnitChoices.choices, default=UnitChoices.kg)
    stock = DecimalField(max_digits=12, decimal_places=1, default=0)

    def __str__(self):
        return f"{self.name} ({self.barcode})"

    LOW_STOCK_THRESHOLDS = {
        'kg': Decimal('5.00'),
        'piece': Decimal('5'),
    }

    def get_low_stock_threshold(self):
        return self.LOW_STOCK_THRESHOLDS.get(self.unit, Decimal('1.00'))

    @property
    def is_low_stock(self):
        return self.stock <= self.get_low_stock_threshold()

    def decrease_stock(self, quantity):
        q = to_decimal(quantity)
        if q <= 0:
            raise ValueError("Quantity must be positive")
        with transaction.atomic():
            # reload to avoid race condition
            prod = Product.objects.select_for_update().get(pk=self.pk)
            if prod.stock < q:
                raise ValueError(f"Insufficient stock: {prod.stock}")
            prod.stock = (prod.stock - q).quantize(CENTS)
            prod.save(update_fields=['stock'])
            return prod.stock

    def increase_stock(self, quantity):
        q = to_decimal(quantity)
        if q <= 0:
            raise ValueError("Quantity must be positive")
        with transaction.atomic():
            prod = Product.objects.select_for_update().get(pk=self.pk)
            prod.stock = (prod.stock + q).quantize(CENTS)
            prod.save(update_fields=['stock'])
            return prod.stock

