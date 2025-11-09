from functools import wraps
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles=None):
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied("Siz login qilmagansiz.")
            if allowed_roles and request.user.role not in allowed_roles:
                raise PermissionDenied("Sizda bu sahifaga kirish huquqi yo‘q.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
