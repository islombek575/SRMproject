from apps.models import SaleItem, Debt
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver


@receiver([post_save, post_delete], sender=SaleItem)
def update_sale_total(sender, instance, **kwargs):
    sale = instance.sale
    total = sum(item.subtotal for item in sale.items.all())
    if sale.total_amount == total:
        return
    sale.total_amount = total
    post_save.disconnect(update_sale_total, sender=SaleItem)
    try:
        sale.save(update_fields=["total_amount"])
    finally:
        post_save.connect(update_sale_total, sender=SaleItem)


@receiver(pre_save, sender=Debt)
def debt_pre_save(sender, instance, **kwargs):
    instance.update_status()


@receiver(post_delete, sender=SaleItem)
def restore_stock_on_delete(sender, instance, **kwargs):
    try:
        instance.product.increase_stock(instance.quantity)
    except Exception:
        pass