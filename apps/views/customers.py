from apps.mixins import RoleRequiredMixin
from apps.models import Customer, Debt
from django.db.models import F, Max
from django.shortcuts import get_object_or_404
from django.views.generic import ListView


class CustomerListView(RoleRequiredMixin, ListView):
    allowed_roles = ['admin']
    model = Customer
    template_name = 'debt/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 10

    def get_queryset(self):
        self.search_query = self.request.GET.get('q', '')
        self.sort_by_debt = self.request.GET.get('sort_by_debt', '')
        self.debt_status = self.request.GET.get('debt_status', '')

        queryset = Customer.objects.all()
        queryset = queryset.annotate(
            last_debt_date=Max('debts__created_at')
        )

        if self.search_query:
            queryset = queryset.filter(name__icontains=self.search_query)

        if self.debt_status == 'has_debt':
            queryset = queryset.filter(total_debt__gt=0)
        elif self.debt_status == 'no_debt':
            queryset = queryset.filter(total_debt=0)

        if self.sort_by_debt == 'max_debt':
            queryset = queryset.order_by('-total_debt')
        elif self.sort_by_debt == 'min_debt':
            queryset = queryset.order_by('total_debt')
        elif self.sort_by_debt == 'latest_debt':
            queryset = queryset.order_by(F('last_debt_date').desc(nulls_last=True))
        else:
            queryset = queryset.order_by('name')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.search_query
        context['sort_by_debt'] = self.sort_by_debt
        context['debt_status'] = self.debt_status
        return context


class CustomerDebtListView(RoleRequiredMixin, ListView):
    allowed_roles = ['admin']
    model = Debt
    template_name = 'debt/customer_debt_list.html'
    context_object_name = 'debts'

    def get_queryset(self):
        self.customer = get_object_or_404(Customer, id=self.kwargs['customer_id'])
        return self.customer.debts.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customer'] = self.customer
        return context
