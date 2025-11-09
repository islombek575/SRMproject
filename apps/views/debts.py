from apps.forms import DebtPaymentForm
from apps.models import Debt
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import FormView


class DebtPaymentView(FormView):
    template_name = 'debt/debt_payment.html'
    form_class = DebtPaymentForm

    def dispatch(self, request, *args, **kwargs):
        self.debt = get_object_or_404(Debt, pk=self.kwargs['debt_pk'])

        if not self.debt.can_pay:
            messages.error(request, "Bu qarz to‘langan, to‘lov qilolmaysiz!")
            return redirect('customer_debt_list', customer_id=self.debt.customer.id)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['debt'] = self.debt
        return context

    def form_valid(self, form):
        amount = form.cleaned_data['amount']

        if amount > self.debt.remaining:
            messages.error(
                self.request,
                f"To‘lov summasi qoldiq qarzdan ({self.debt.remaining} so‘m) katta bo‘la olmaydi!"
            )
            return self.form_invalid(form)

        self.debt.paid_amount += amount
        self.debt.customer.total_debt -= amount
        self.debt.status = 'paid' if self.debt.paid_amount >= self.debt.amount else 'partial'

        self.debt.customer.save()
        self.debt.save()

        messages.success(self.request, f"{amount} so‘m muvaffaqiyatli to‘landi!")
        return super().form_valid(form)

    def get_success_url(self):
        return redirect('customer_debt_list', customer_id=self.debt.customer.id).url
