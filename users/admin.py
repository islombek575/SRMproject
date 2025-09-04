from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User



@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("id", "username", "full_name", "is_staff", "last_login")

