from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from apps.forms import EmployeeForm
from apps.mixins import RoleRequiredMixin

User = get_user_model()


class EmployeeListView(RoleRequiredMixin, View):
    allowed_roles = ['admin']

    def get(self, request, *args, **kwargs):
        employees = User.objects.filter(is_staff=True)
        return render(request, 'employees/list.html', {'employees': employees})


class EmployeeAddView(RoleRequiredMixin, View):
    allowed_roles = ['admin']

    def get(self, request, *args, **kwargs):
        form = EmployeeForm()
        return render(request, 'employees/form.html', {'form': form, 'title': 'Xodim qo‘shish'})

    def post(self, request, *args, **kwargs):
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Xodim muvaffaqiyatli qo‘shildi.')
            return redirect('employee_list')
        else:
            messages.error(request, "Forma to'g'ri to'ldirilmagan")
        return render(request, 'employees/form.html', {'form': form, 'title': 'Xodim qo‘shish'})


class EmployeeUpdateView(RoleRequiredMixin, View):
    allowed_roles = ['admin']

    def get(self, request, pk, *args, **kwargs):
        employee = get_object_or_404(User, pk=pk)
        form = EmployeeForm(instance=employee)
        return render(request, 'employees/form.html', {'form': form, 'title': 'Xodimni tahrirlash'})

    def post(self, request, pk, *args, **kwargs):
        employee = get_object_or_404(User, pk=pk)
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Xodim ma‘lumotlari yangilandi.')
            return redirect('employee_list')
        return render(request, 'employees/form.html', {'form': form, 'title': 'Xodimni tahrirlash'})


class EmployeeDeleteView(RoleRequiredMixin, View):
    allowed_roles = ['admin']

    def get(self, request, pk, *args, **kwargs):
        employee = get_object_or_404(User, pk=pk)
        return render(request, 'employees/confirm_delete.html', {'employee': employee})

    def post(self, request, pk, *args, **kwargs):
        employee = get_object_or_404(User, pk=pk)
        employee.delete()
        messages.success(request, 'Xodim o‘chirildi.')
        return redirect('employee_list')
