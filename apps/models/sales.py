from decimal import Decimal

from django.db import transaction

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

from apps.utils import to_decimal

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

    def recalc_total(self):
        total = sum((item.subtotal for item in self.items.all()), Decimal('0.00'))
        self.total_amount = to_decimal(total)
        return self.total_amount

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.recalc_total()
        super().save(update_fields=['total_amount'])
        # update customer debt only for credit sales
        if self.payment_type == Sale.PAYMENT.CREDIT and self.customer:
            self.customer.total_debt = to_decimal(self.customer.total_debt) + (self.total_amount - to_decimal(self.paid_amount))
            self.customer.save(update_fields=['total_debt'])


    def __str__(self):
            return f"Sale #{self.id} - Total: {self.total_amount}, Remaining: {self.total_amount - self.paid_amount}"


class SaleItem(Model):
    sale = ForeignKey('apps.Sale', on_delete=CASCADE, related_name='items')
    product = ForeignKey('apps.Product', on_delete=SET_NULL, null=True)
    quantity = DecimalField(max_digits=10, decimal_places=2)
    price = DecimalField(max_digits=12, decimal_places=2)

    @property
    def subtotal(self):
        return to_decimal(self.quantity) * to_decimal(self.price)

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        with transaction.atomic():
            if is_new:
                self.product.decrease_stock(self.quantity)
            super().save(*args, **kwargs)
            self.sale.recalc_total()
            self.sale.save(update_fields=['total_amount'])