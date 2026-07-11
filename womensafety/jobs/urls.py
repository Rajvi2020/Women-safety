from django.urls import path
from . import views

urlpatterns = [
    path('jobs/', views.job_list_view, name='jobs'),
    path('jobs/<int:pk>/', views.job_detail_view, name='job_detail'),
    path('jobs/<int:pk>/apply/', views.apply_job_view, name='apply_job'),
    path('jobs/saved/', views.saved_jobs_view, name='saved_jobs'),
    path('jobs/<int:pk>/save/', views.toggle_save_job_api, name='save_job'),
]
