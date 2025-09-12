from django.db.models.signals import post_save
from django.dispatch import receiver
from sales.models import Sale
from credits.models import Credit


@receiver(post_save, sender=Sale)
def create_credit_for_sale(sender, instance, created, **kwargs):
    if created and instance.payment_type == "credit":
        if instance.paid_amount < instance.total_amount:
            Credit.objects.create(
                sale=instance,
                customer=instance.customer,
                paid_amount=instance.paid_amount,
                seller=instance.seller,
                amount=instance.total_amount,
                created_at=instance.created_at,
                status="partial",
            )
        elif instance.paid_amount == instance.total_amount:
            Credit.objects.create(
                sale=instance,
                customer=instance.customer,
                paid_amount=instance.paid_amount,
                seller=instance.seller,
                amount=instance.total_amount,
                created_at=instance.created_at,
                status="paid",
            )
        elif instance.paid_amount == 0:
            Credit.objects.create(
                sale=instance,
                customer=instance.customer,
                paid_amount=instance.paid_amount,
                seller=instance.seller,
                amount=instance.total_amount,
                created_at=instance.created_at,
                status="outstanding",
            )
