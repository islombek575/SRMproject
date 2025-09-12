from django import forms
from credits.models import Credit, CreditPayment

class CreditForm(forms.ModelForm):
    class Meta:
        model = Credit
        fields = ["sale", "customer", "amount", "due_date", "status", "notes"]

class CreditPaymentForm(forms.ModelForm):
    class Meta:
        model = CreditPayment
        fields = ["amount", "note"]
