from django.urls import path
from . import views

urlpatterns = [
    path('resources/', views.resources_view, name='resources'),
]
