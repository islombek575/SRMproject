from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from apps.forms import DebtPaymentForm
from apps.mixins import RoleRequiredMixin
from apps.models import Customer, Debt


class CustomerListView(View, RoleRequiredMixin):
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('q', '')
        if search_query:
            customers = Customer.objects.filter(name__icontains=search_query)
        else:
            customers = Customer.objects.all()

        for c in customers:
            debts = c.debts.all()
            c.total_debt = sum(d.remaining for d in debts)
            c.has_debt = c.total_debt > 0
            last_debt = debts.order_by('-created_at').first()
            c.last_debt_date = last_debt.created_at if last_debt else None

        return render(request, 'debt/customer_list.html', {
            'customers': customers,
            'search_query': search_query
        })


class CustomerDebtListView(View, RoleRequiredMixin):
    def get(self, request, customer_id, *args, **kwargs):
        customer = get_object_or_404(Customer, id=customer_id)
        debts = customer.debts.all().order_by('-created_at')
        return render(request, 'debt/customer_debt_list.html', {'customer': customer, 'debts': debts})


class DebtPaymentView(View, RoleRequiredMixin):
    def get(self, request, debt_pk, *args, **kwargs):
        debt = get_object_or_404(Debt, pk=debt_pk)
        if not debt.can_pay:
            messages.error(request, "Bu qarz to‘langan, to‘lov qilolmaysiz!")
            return redirect('customer_debt_list', customer_id=debt.customer.id)

        form = DebtPaymentForm()
        return render(request, 'debt/debt_payment.html', {'form': form, 'debt': debt})

    def post(self, request, debt_pk, *args, **kwargs):
        debt = get_object_or_404(Debt, pk=debt_pk)
        if not debt.can_pay:
            messages.error(request, "Bu qarz to‘langan, to‘lov qilolmaysiz!")
            return redirect('customer_debt_list', customer_id=debt.customer.id)

        form = DebtPaymentForm(request.POST)

        if form.is_valid():
            amount = form.cleaned_data['amount']
            if amount > debt.remaining:
                messages.error(request, f"To‘lov summasi qoldiq qarzdan ({debt.remaining} so‘m) katta bo‘la olmaydi!")
            else:
                debt.paid_amount += amount
                debt.customer.total_debt -= amount
                debt.status = 'paid' if debt.paid_amount >= debt.amount else 'partial'
                debt.customer.save()
                debt.save()
                messages.success(request, f"{amount} so‘m muvaffaqiyatli to‘landi!")
                return redirect('customer_debt_list', customer_id=debt.customer.id)

        return render(request, 'debt/debt_payment.html', {'form': form, 'debt': debt})
