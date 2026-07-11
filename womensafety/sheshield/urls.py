"""
URL configuration for sheshield project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('dashboard.urls')),
    path('', include('profile.urls')),
    path('', include('safety.urls')),
    path('', include('career.urls')),
    path('', include('mentor.urls')),
    path('', include('jobs.urls')),
    path('', include('scholarships.urls')),
    path('', include('resources.urls')),
    path('', include('notifications.urls')),
    path('', include('adminpanel.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
