from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("seller", "Seller"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="seller")

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def full_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username
