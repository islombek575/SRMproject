from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class DebtPaymentForm(forms.Form):
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0.01, label="To'lov summasi",
                                widget=forms.NumberInput(attrs={
                                    'class': 'border-2 border-gray-300 rounded-lg px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
                                })
                                )


class EmployeeForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password', 'is_staff', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


from django import forms
from apps.models.products import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'barcode', 'cost_price', 'sell_price', 'stock', 'unit']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'barcode': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'cost_price': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
            'sell_price': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
            'unit': forms.Select(
                choices=Product.UNIT_CHOICES,
                attrs={'class': 'w-full p-2 border rounded'}
            ),
            'stock': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
        }


from django import forms
from apps.models import PurchaseItem


class PurchaseForm(forms.ModelForm):
    product_name = forms.CharField(max_length=255, label="Mahsulot nomi yoki barcode")

    class Meta:
        model = PurchaseItem
        fields = ['product_name', 'quantity', 'cost_price']

    def clean(self):
        cleaned_data = super().clean()
        name_or_barcode = cleaned_data.get('product_name')

        if name_or_barcode:
            product, created = Product.objects.get_or_create(
                name=name_or_barcode,
                defaults={'barcode': name_or_barcode, 'cost_price': cleaned_data.get('cost_price', 0),
                          'sell_price': cleaned_data.get('cost_price', 0) * 1.2}
            )
            cleaned_data['product'] = product

        return cleaned_data


from django import forms

from apps.models import Sale, Product


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ["payment_type", "customer"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["customer"].required = False


class SaleItemForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), label="Mahsulot")
    quantity = forms.IntegerField(min_value=1, label="Miqdor")


from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "w-full p-2 border rounded-lg",
            "placeholder": "Foydalanuvchi nomi"
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "w-full p-2 border rounded-lg",
            "placeholder": "Parol"
        })
    )


from django import forms
from django.contrib.auth.forms import PasswordChangeForm


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Eski parol",
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none transition"
        })
    )
    new_password1 = forms.CharField(
        label="Yangi parol",
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none transition"
        })
    )
    new_password2 = forms.CharField(
        label="Yangi parol (takror)",
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none transition"
        })
    )
