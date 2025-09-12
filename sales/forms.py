# sales/forms.py
from django import forms

class AddProductForm(forms.Form):
    barcode = forms.CharField(
        label="Shtrixkod",
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Barcode skaner qiling"})
    )
    quantity = forms.IntegerField(
        label="Soni",
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
