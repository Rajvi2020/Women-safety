from django.urls import path
from . import views

urlpatterns = [
    path('career/chat/', views.career_chat_view, name='career_chat'),
    path('career/chat/send/', views.career_chat_send_view, name='career_chat_send'),
    path('career/roadmap/', views.career_roadmap_view, name='career_roadmap'),
    path('career/roadmap/step/<int:pk>/update/', views.update_roadmap_step_api, name='update_roadmap_step'),
    path('career/resume-review/', views.resume_review_view, name='resume_review'),
    path('career/resume-review/submit/', views.resume_review_submit_view, name='resume_review_submit'),
    path('career/interview-prep/', views.interview_prep_view, name='interview_prep'),
]
