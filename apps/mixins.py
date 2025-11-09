from django.core.exceptions import PermissionDenied

class RoleRequiredMixin:
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("Siz login qilmagansiz.")
        if self.allowed_roles and request.user.role not in self.allowed_roles:
            raise PermissionDenied("Sizda bu sahifaga kirish huquqi yo‘q.")
        return super().dispatch(request, *args, **kwargs)
