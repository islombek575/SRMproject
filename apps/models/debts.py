from decimal import Decimal

from apps.models.base import CreatedBaseModel, UUIDBaseModel
from apps.models.customers import Customer
from django.db.models import CASCADE, CharField, DecimalField, ForeignKey, TextChoices


class Debt(CreatedBaseModel, UUIDBaseModel):
    class StatusChoices(TextChoices):
        UNPAID = 'UNPAID', "To'lanmagan"
        PARTIAL = 'PARTIAL', "Qisman to'langan"
        PAID = 'PAID', "To'langan"

    customer = ForeignKey(Customer, on_delete=CASCADE, related_name='debts')
    amount = DecimalField(max_digits=12, decimal_places=2)
    paid_amount = DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    status = CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.UNPAID)
    created_by = ForeignKey('apps.User', on_delete=CASCADE, related_name='debt_created_by')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Debt'
        verbose_name_plural = 'Debts'

    def __str__(self):
        return f"{self.customer.name} - {self.amount}"

    @property
    def can_pay(self):
        return self.status in ['UNPAID', 'PARTIAL']

    @property
    def remaining(self):
        return self.amount - self.paid_amount or Decimal(0.00)

    def update_status(self):
        if self.paid_amount == 0:
            self.status = self.StatusChoices.PAID
        elif self.paid_amount < self.amount:
            self.status = self.StatusChoices.PARTIAL
        else:
            self.status = self.StatusChoices.UNPAID
        self.save()
