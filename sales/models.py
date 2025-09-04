import uuid

from django.db.models import Model, UUIDField, ForeignKey, SET_NULL, DecimalField, DateTimeField, CharField, \
    PositiveIntegerField, CASCADE
from django.utils import timezone

from customers.models import Customer


class Sale(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = ForeignKey(Customer,on_delete=SET_NULL,related_name="sales",blank=True,null=True)
    total_amount = DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Sale {self.id} - {self.customer.name if self.customer else 'Umumiy'}"

    def calculate_total(self):
        total = sum(item.subtotal for item in self.items.all())
        self.total_amount = total
        self.save()
        return total


class SaleItem(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale = ForeignKey(Sale, related_name="items", on_delete=CASCADE)
    product_name = CharField(max_length=255)
    price = DecimalField(max_digits=12, decimal_places=2)
    quantity = PositiveIntegerField(default=1)
    subtotal = DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"