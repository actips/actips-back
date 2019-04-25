from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'api/admin/', include('api_admin.urls', namespace='api_admin')),
    path(r'api/client/', include('api_client.urls', namespace='api_client')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
