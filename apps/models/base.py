import uuid

from django.db.models import CharField, DateTimeField, Model, UUIDField


class CreatedBaseModel(Model):
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class SlugBaseModel(Model):
    slug = CharField(max_length=10, unique=True)

    class Meta:
        abstract = True


class UUIDBaseModel(Model):
    id = UUIDField(default=uuid.uuid4, editable=False, primary_key=True)

    class Meta:
        abstract = True
