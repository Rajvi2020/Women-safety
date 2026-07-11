"""
SheShield AI — Core App URL Configuration
All application routes.
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    # ── Auth ──────────────────────────────────────────────
    path('', views.home_redirect, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/', views.reset_password_view, name='reset_password'),

    # ── Dashboard ─────────────────────────────────────────
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # ── Profile ───────────────────────────────────────────
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/education/add/', views.add_education_view, name='add_education'),
    path('profile/resume/upload/', views.upload_resume_view, name='upload_resume'),

    # ── Safety ────────────────────────────────────────────
    path('safety/sos/', views.sos_view, name='sos'),
    path('safety/sos/trigger/', views.sos_trigger_view, name='sos_trigger'),
    path('safety/contacts/', views.emergency_contacts_view, name='emergency_contacts'),
    path('safety/contacts/add/', views.add_contact_view, name='add_contact'),
    path('safety/contacts/<int:pk>/delete/', views.delete_contact_view, name='delete_contact'),
    path('safety/live-location/', views.live_location_view, name='live_location'),
    path('safety/safe-route/', views.safe_route_view, name='safe_route'),

    # ── Career ────────────────────────────────────────────
    path('career/chat/', views.career_chat_view, name='career_chat'),
    path('career/chat/send/', views.career_chat_send_view, name='career_chat_send'),
    path('career/roadmap/', views.career_roadmap_view, name='career_roadmap'),
    path('career/resume-review/', views.resume_review_view, name='resume_review'),
    path('career/resume-review/submit/', views.resume_review_submit_view, name='resume_review_submit'),
    path('career/interview-prep/', views.interview_prep_view, name='interview_prep'),

    # ── Mentors ───────────────────────────────────────────
    path('mentors/', views.mentor_list_view, name='mentors'),
    path('mentors/<int:pk>/', views.mentor_detail_view, name='mentor_detail'),
    path('mentors/book/', views.book_session_view, name='book_session'),

    # ── Jobs ──────────────────────────────────────────────
    path('jobs/', views.job_list_view, name='jobs'),
    path('jobs/<int:pk>/', views.job_detail_view, name='job_detail'),
    path('jobs/<int:pk>/apply/', views.apply_job_view, name='apply_job'),

    # ── Scholarships ──────────────────────────────────────
    path('scholarships/', views.scholarship_list_view, name='scholarships'),
    path('scholarships/<int:pk>/', views.scholarship_detail_view, name='scholarship_detail'),

    # ── Resources ─────────────────────────────────────────
    path('resources/', views.resources_view, name='resources'),

    # ── Notifications ─────────────────────────────────────
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),

    # ── Settings ──────────────────────────────────────────
    path('settings/', views.settings_view, name='settings'),
    path('settings/password/', views.change_password_view, name='change_password'),
    path('settings/delete-account/', views.delete_account_view, name='delete_account'),

    # ── Admin ─────────────────────────────────────────────
    path('admin-panel/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-panel/users/', views.admin_users_view, name='admin_users'),
    path('admin-panel/users/<int:pk>/', views.admin_user_detail_view, name='admin_user_detail'),
    path('admin-panel/users/export/', views.admin_export_users_view, name='admin_export_users'),
    path('admin-panel/mentors/', views.admin_mentors_view, name='admin_mentors'),
    path('admin-panel/mentors/<int:pk>/approve/', views.admin_approve_mentor_view, name='admin_approve_mentor'),
    path('admin-panel/mentors/<int:pk>/reject/', views.admin_reject_mentor_view, name='admin_reject_mentor'),
    path('admin-panel/jobs/', views.admin_jobs_view, name='admin_jobs'),
    path('admin-panel/scholarships/', views.admin_scholarships_view, name='admin_scholarships'),
    path('admin-panel/resources/', views.admin_resources_view, name='admin_resources'),
    path('admin-panel/sos/', views.admin_sos_view, name='admin_sos'),
    path('admin-panel/sos/<int:pk>/resolve/', views.admin_resolve_sos_view, name='admin_resolve_sos'),
    path('admin-panel/reports/', views.admin_reports_view, name='admin_reports'),
]
