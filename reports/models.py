import uuid

from django.db.models import Model, UUIDField, DateField, DecimalField,PositiveIntegerField
from django.utils import timezone

from sales.models import Sale


class Report(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = DateField(default=timezone.now)
    total_sales = DecimalField(max_digits=12, decimal_places=2, default=0)
    total_transactions = PositiveIntegerField(default=0)
    

    def __str__(self):
        return f"Report {self.date}"

    @classmethod
    def generate_daily(cls, date=None):
        if not date:
            date = timezone.now().date()
        sales = Sale.objects.filter(created_at__date=date)
        total = sum(s.total_amount for s in sales)
        report, created = cls.objects.get_or_create(date=date)
        report.total_sales = total
        report.total_transactions = sales.count()
        report.save()
        return report