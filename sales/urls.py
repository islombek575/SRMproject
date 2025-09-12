from django.urls import path

from . import views
from .views import finish_sale

app_name = "sales"

urlpatterns = [
    path("create/", views.create_sale, name="create_sale"),
    path('<uuid:sale_id>/finish/', finish_sale, name='finish_sale'),
]
