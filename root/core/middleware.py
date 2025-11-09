from django.conf import settings
from django.shortcuts import redirect

EXEMPT_URLS = [
    settings.LOGIN_URL,
    '/users/logout/',
    '/register/',
    '/admin/',
]

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info
        if not request.user.is_authenticated and not any(path.startswith(url) for url in EXEMPT_URLS):
            return redirect(settings.LOGIN_URL)
        return self.get_response(request)
