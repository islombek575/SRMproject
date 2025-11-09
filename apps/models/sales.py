import uuid
from decimal import Decimal

from django.conf import settings
from django.db.models import Model, UUIDField, ForeignKey, CharField, DecimalField, DateTimeField, PositiveIntegerField, \
    CASCADE, SET_NULL
from django.db.models.enums import TextChoices

from apps.models import Customer
from apps.models import Product

User = settings.AUTH_USER_MODEL

class Sale(Model):
    class PAYMENT(TextChoices):
        CASH = 'cash', 'Naqd'
        CARD = 'card', 'Karta'
        CREDIT = 'credit', 'Karta'

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

    def subtotal(self):
        return Decimal(self.quantity) * self.price
