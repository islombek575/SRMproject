from django.contrib.auth.models import AbstractUser
from django.db.models import CharField


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('cashier', 'Cashier'),
    )
    role = CharField(max_length=20, choices=ROLE_CHOICES, default='cashier')

    def is_cashier(self):
        return self.role == 'cashier'

    def is_admin(self):
        return self.role == 'admin'
