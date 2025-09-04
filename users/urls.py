from django.urls import path

from .views import UserProfileTemplateView, user_login, user_logout

urlpatterns = [
    path('login/', user_login, name='user_login'),
    path('profile/', UserProfileTemplateView.as_view(), name='user_profile'),
    path('logout/', user_logout, name='logout_page'),
]
