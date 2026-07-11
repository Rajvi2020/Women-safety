from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/education/add/', views.add_education_view, name='add_education'),
    path('profile/resume/upload/', views.upload_resume_view, name='upload_resume'),
    path('profile/skill/add/', views.add_skill_view, name='add_skill'),
    path('profile/skill/<int:pk>/delete/', views.delete_skill_view, name='delete_skill'),
]
