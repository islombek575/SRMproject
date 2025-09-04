from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from users.forms import LoginForm


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("dashboard_view")  # login bo‘lsa dashboardga
            else:
                return render(request, "users/login.html", {
                    "form": form,
                    "error": "Login yoki parol noto‘g‘ri!"
                })
    else:
        form = LoginForm()
    return render(request, "users/login.html", {"form": form})




@login_required(login_url="user_login")
def user_logout(request):
    logout(request)
    return redirect("user_login")   # 🚀 logoutdan keyin login sahifaga qaytadi


class UserProfileTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'


@login_required(login_url='user_login')
def dashboard_view(request):
    return render(request, "inventory/dashboard.html")
