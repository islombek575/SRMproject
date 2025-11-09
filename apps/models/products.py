import uuid
from decimal import Decimal

from django.db.models import CharField, DateTimeField, DecimalField, Model, TextChoices, UUIDField


class Product(Model):
    class UnitChoices(TextChoices):
        piece = "piece", "Dona"
        kg = "kg", "Kilogram"

    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = CharField(max_length=255)
    barcode = CharField(max_length=50, unique=True)
    cost_price = DecimalField(max_digits=12, decimal_places=2)
    sell_price = DecimalField(max_digits=12, decimal_places=2)
    unit = CharField(max_length=10, choices=UnitChoices.choices, default=UnitChoices.kg)
    stock = DecimalField(max_digits=12, decimal_places=1, default=0)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.barcode})"

    @property
    def profit(self):
        return self.sell_price - self.cost_price

    @property
    def is_low_stock(self):
        threshold = Decimal('1.00') if self.unit == 'kg' else Decimal('5.00')
        return self.stock <= threshold

    def decrease_stock(self, quantity):
        if quantity > self.stock:
            raise ValueError(f"Yetarli {self.get_unit_display()} yo‘q: {self.stock}")
        self.stock -= Decimal(quantity)
        self.save(update_fields=['stock'])

    def increase_stock(self, quantity):
        self.stock += Decimal(quantity)
        self.save(update_fields=['stock'])
