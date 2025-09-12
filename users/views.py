from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView

from users.forms import LoginForm

User = get_user_model()


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("inventory:dashboard_view")
            else:
                return render(request, "users/login.html", {
                    "form": form,
                    "error": "Login yoki parol noto‘g‘ri!"
                })
    else:
        form = LoginForm()
    return render(request, "users/login.html", {"form": form})


@login_required(login_url="users:user_login")
def user_logout(request):
    logout(request)
    return redirect("users:user_login")  # 🚀 logoutdan keyin login sahifaga qaytadi


class UserProfileTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'


@login_required(login_url='users:user_login')
def dashboard_view(request):
    return render(request, "inventory/dashboard.html")


# Faqat admin foydalanuvchilar kirishi uchun decorator
def admin_required(view_func):
    decorated_view_func = login_required(user_passes_test(lambda u: u.is_superuser)(view_func))
    return decorated_view_func


# Foydalanuvchilar ro'yxati
@admin_required
def user_list(request):
    current_user = request.user
    users = User.objects.all()
    return render(request, 'users/user-list.html', {'users': users, 'user_id': current_user.id})


# Foydalanuvchi qo'shish
@admin_required
def user_add(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        is_staff = request.POST.get("is_staff") == "on"
        is_superuser = request.POST.get("is_superuser") == "on"

        if username and password:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            user.save()
            messages.success(request, f"{username} qo‘shildi!")
            return redirect("users:user_list")
        else:
            messages.error(request, "Iltimos, username va password kiriting!")

    return render(request, 'users/user-form.html', {"action": "Qo‘shish"})


# Foydalanuvchi update
@admin_required
def user_update(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")
        password = request.POST.get("password")
        if password:
            user.set_password(password)
        user.is_staff = request.POST.get("is_staff") == "on"
        user.is_superuser = request.POST.get("is_superuser") == "on"
        user.save()
        messages.success(request, f"{user.username} yangilandi!")
        return redirect("users:user_list")

    return render(request, 'users/user-form.html', {"user": user, "action": "Yangilash"})


# Foydalanuvchi o'chirish
@admin_required
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, f"{user.username} o‘chirildi!")
    return redirect("users:user_list")
