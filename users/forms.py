from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(
        label="Login",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Login"})
    )
    password = forms.CharField(
        label="Parol",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Parol"})
    )
