from django.conf import settings
from django.conf.urls import handler404
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from export_lsd.views import error_404


urlpatterns = [
    path('', include('homepage.urls')),
    path('admin/', admin.site.urls),
    path('export-lsd/', include('export_lsd.urls', namespace='export_lsd')),
    path('login/', include('login.urls')),
    path('siradig/', include('reader.urls')),
    path('users/', include('users.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.TEMP_URL, document_root=settings.TEMP_ROOT)

handler404 = error_404
