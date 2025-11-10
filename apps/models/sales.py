from decimal import Decimal

from apps.models.base import UUIDBaseModel
from django.conf import settings
from django.db.models import (
    CASCADE,
    SET_NULL,
    CharField,
    DateTimeField,
    DecimalField,
    ForeignKey,
    Model,
)
from django.db.models.enums import TextChoices

User = settings.AUTH_USER_MODEL


class Sale(UUIDBaseModel):
    class PAYMENT(TextChoices):
        CASH = 'cash', 'Naqd'
        CARD = 'card', 'Karta'
        CREDIT = 'credit', 'Nasiya'

    customer = ForeignKey('apps.Customer', on_delete=SET_NULL, null=True, blank=True)
    cashier = ForeignKey('apps.User', on_delete=SET_NULL, null=True, blank=True)
    payment_type = CharField(max_length=10, choices=PAYMENT.choices, default=PAYMENT.CASH)
    total_amount = DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    paid_amount = DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale #{self.id} - Total: {self.total_amount}, Remaining: {self.total_amount - self.paid_amount}"


class SaleItem(Model):
    sale = ForeignKey('apps.Sale', on_delete=CASCADE, related_name='items')
    product = ForeignKey('apps.Product', on_delete=SET_NULL, null=True)
    quantity = DecimalField(max_digits=10, decimal_places=2)
    price = DecimalField(max_digits=12, decimal_places=2)

    @property
    def subtotal(self):
        return (self.quantity * self.price).quantize(Decimal("0.01"))

    def save(self, *args, **kwargs):
        if not self.pk:
            self.product.decrease_stock(self.quantity)
        super().save(*args, **kwargs)
