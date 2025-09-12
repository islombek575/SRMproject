from django.urls import path

from .views import UserProfileTemplateView, user_login, user_logout, user_list, user_add, user_update, user_delete

app_name = "users"

urlpatterns = [
    path('login/', user_login, name='user_login'),
    path('profile/', UserProfileTemplateView.as_view(), name='user_profile'),
    path('logout/', user_logout, name='logout_page'),
    path('', user_list, name='user_list'),
    path('add/', user_add, name='user_add'),
    path('update/<int:user_id>/', user_update, name='user_update'),
    path('delete/<int:user_id>/', user_delete, name='user_delete'),
]
