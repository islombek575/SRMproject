from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from root.settings import MEDIA_ROOT, MEDIA_URL

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.urls')),
] + static(MEDIA_URL, document_root=MEDIA_ROOT)


def redirect_root(request, exception):
    return redirect('dashboard')


handler404 = redirect_root
