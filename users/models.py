from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    @property
    def full_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username
