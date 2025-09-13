from django.urls import path
from .views import UserLoginView, UserLogoutView
from django.conf.urls.static import static

from root.settings import MEDIA_URL, MEDIA_ROOT, STATIC_URL, STATIC_ROOT


app_name = "users"

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
]+ static(MEDIA_URL, document_root=MEDIA_ROOT) + static(STATIC_URL, document_root=STATIC_ROOT)

