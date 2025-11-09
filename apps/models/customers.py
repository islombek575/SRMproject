from decimal import Decimal

from django.db.models import Model, CharField, DecimalField, DateTimeField


class Customer(Model):
    name = CharField(max_length=150)
    total_debt = DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
