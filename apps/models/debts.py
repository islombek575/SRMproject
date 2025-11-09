import uuid
from decimal import Decimal

from apps.models.customers import Customer
from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    DecimalField,
    ForeignKey,
    Model,
    UUIDField,
)


class Debt(Model):
    STATUS_CHOICES = [
        ('unpaid', "To'lanmagan"),
        ('partial', "Qisman to'langan"),
        ('paid', "To'langan"),
    ]
    id = UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    customer = ForeignKey(Customer, on_delete=CASCADE, related_name='debts')
    amount = DecimalField(max_digits=12, decimal_places=2)
    paid_amount = DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    status = CharField(max_length=10, choices=STATUS_CHOICES, default='unpaid')
    created_by = ForeignKey('apps.User', on_delete=CASCADE, related_name='debt_created_by')
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Debt'
        verbose_name_plural = 'Debts'

    def __str__(self):
        return f"{self.customer.name} - {self.amount}"

    @property
    def can_pay(self):
        return self.status in ['unpaid', 'partial']

    @property
    def remaining(self):
        return self.amount - self.paid_amount or Decimal(0.00)

    def update_status(self):
        if self.paid_amount == 0:
            self.status = 'unpaid'
        elif self.paid_amount < self.amount:
            self.status = 'partial'
        else:
            self.status = 'paid'
        self.save()
