from django.urls import path
from . import views

urlpatterns = [
    path('mentors/', views.mentor_list_view, name='mentors'),
    path('mentors/<int:pk>/', views.mentor_detail_view, name='mentor_detail'),
    path('mentors/book/', views.book_session_view, name='book_session'),
    path('mentors/requests/', views.mentorship_requests_view, name='mentorship_requests'),
    path('mentors/requests/<int:pk>/<str:status>/', views.update_session_status_view, name='update_session_status'),
]
