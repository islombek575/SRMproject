import uuid

from django.db.models import Model, UUIDField, CharField, DateTimeField


class Customer(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CharField(max_length=255, blank=True, null=True)
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name if self.name else "Noma'lum mijoz"