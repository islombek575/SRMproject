import uuid
from decimal import Decimal

from apps.models import Customer, Product
from django.conf import settings
from django.db.models import (
    CASCADE,
    SET_NULL,
    CharField,
    DateTimeField,
    DecimalField,
    ForeignKey,
    Model,
    PositiveIntegerField,
    UUIDField,
)
from django.db.models.enums import TextChoices

User = settings.AUTH_USER_MODEL

class Sale(Model):
    class PAYMENT(TextChoices):
        CASH = 'cash', 'Naqd'
        CARD = 'card', 'Karta'
        CREDIT = 'credit', 'Nasiya'

    id = UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=True)
    customer = ForeignKey(Customer, on_delete=SET_NULL, null=True, blank=True)
    cashier = ForeignKey(User, on_delete=SET_NULL, null=True, blank=True)
    payment_type = CharField(max_length=10, choices=PAYMENT.choices, default=PAYMENT.CASH)
    total_amount = DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    paid_amount = DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale #{self.id} - {self.total_amount}"

class SaleItem(Model):
    sale = ForeignKey(Sale, on_delete=CASCADE, related_name='items')
    product = ForeignKey(Product, on_delete=SET_NULL, null=True)
    quantity = PositiveIntegerField()
    price = DecimalField(max_digits=12, decimal_places=2)

    @property
    def subtotal(self):
        return Decimal(self.quantity) * self.price
