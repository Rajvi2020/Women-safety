from django.urls import path
from . import views

urlpatterns = [
    path('scholarships/', views.scholarship_list_view, name='scholarships'),
    path('scholarships/<int:pk>/', views.scholarship_detail_view, name='scholarship_detail'),
]
