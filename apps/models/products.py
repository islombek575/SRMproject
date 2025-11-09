import uuid

from django.db.models import Model, CharField, UUIDField, ForeignKey, SET_NULL, DecimalField, DateTimeField

class Product(Model):
    UNIT_CHOICES = [
        ("piece", "Dona"),
        ("kg", "Kilogram"),
    ]

    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = CharField(max_length=255)
    barcode = CharField(max_length=50, unique=True)
    cost_price = DecimalField(max_digits=12, decimal_places=2)
    sell_price = DecimalField(max_digits=12, decimal_places=2)
    unit = CharField(max_length=10, choices=UNIT_CHOICES, default="piece")
    stock = DecimalField(max_digits=12, decimal_places=1, default=0)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def is_low_stock(self):
        return self.stock <= 5

    def __str__(self):
        return f"{self.name} ({self.barcode})"
