from apps.forms import EmployeeForm
from apps.mixins import RoleRequiredMixin
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

User = get_user_model()


class EmployeeListView(RoleRequiredMixin, ListView):
    allowed_roles = ['admin']
    model = User
    template_name = 'employees/list.html'
    context_object_name = 'employees'

    def get_queryset(self):
        return self.model.objects.filter(is_staff=True).order_by('first_name')


class EmployeeAddView(RoleRequiredMixin, CreateView):
    allowed_roles = ['admin']
    model = User
    form_class = EmployeeForm
    template_name = 'employees/form.html'
    success_url = reverse_lazy('employee_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Xodim qo‘shish'
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Xodim muvaffaqiyatli qo‘shildi.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Forma to'g'ri to'ldirilmagan")
        return super().form_invalid(form)


class EmployeeUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ['admin']
    model = User
    form_class = EmployeeForm
    template_name = 'employees/form.html'
    success_url = reverse_lazy('employee_list')
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Xodimni tahrirlash'
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Xodim ma‘lumotlari yangilandi.')
        return response


class EmployeeDeleteView(RoleRequiredMixin, DeleteView):
    allowed_roles = ['admin']
    model = User
    template_name = 'employees/confirm_delete.html'
    success_url = reverse_lazy('employee_list')
    context_object_name = 'employee'
    pk_url_kwarg = 'pk'

    def post(self, request, *args, **kwargs):
        messages.success(request, 'Xodim o‘chirildi.')
        return super().post(request, *args, **kwargs)
