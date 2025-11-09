from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import SaleItem


@receiver([post_save, post_delete], sender=SaleItem)
def update_sale_total(sender, instance, **kwargs):
    sale = instance.sale
    total = sum(item.subtotal() for item in sale.items.all())
    sale.total_amount = total
    sale.save(update_fields=["total_amount"])
