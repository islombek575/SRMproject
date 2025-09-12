from django.urls import path
from . import views

app_name = "credits"

urlpatterns = [
    path("", views.credit_list, name="credit_list"),
    path("<uuid:pk>/", views.credit_detail, name="credit_detail"),
]
