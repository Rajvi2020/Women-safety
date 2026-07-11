from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('adminpanel/', views.admin_dashboard_view, name='admin_dashboard'),

    # User Management
    path('adminpanel/users/', views.admin_users_view, name='admin_users'),
    path('adminpanel/users/<int:pk>/', views.admin_user_detail_view, name='admin_user_detail'),
    path('adminpanel/users/export/', views.admin_export_users_view, name='admin_export_users'),
    path('adminpanel/users/<int:pk>/delete/', views.admin_user_delete_view, name='admin_user_delete'),
    path('adminpanel/users/<int:pk>/toggle-active/', views.admin_user_toggle_active_view, name='admin_user_toggle_active'),

    # Mentor Approvals
    path('adminpanel/mentors/', views.admin_mentors_view, name='admin_mentors'),
    path('adminpanel/mentors/<int:pk>/approve/', views.admin_approve_mentor_view, name='admin_approve_mentor'),
    path('adminpanel/mentors/<int:pk>/reject/', views.admin_reject_mentor_view, name='admin_reject_mentor'),

    # Job Management
    path('adminpanel/jobs/', views.admin_jobs_view, name='admin_jobs'),
    path('adminpanel/jobs/<int:pk>/edit/', views.admin_job_edit_view, name='admin_job_edit'),
    path('adminpanel/jobs/<int:pk>/delete/', views.admin_job_delete_view, name='admin_job_delete'),

    # Scholarship Management
    path('adminpanel/scholarships/', views.admin_scholarships_view, name='admin_scholarships'),
    path('adminpanel/scholarships/<int:pk>/delete/', views.admin_scholarship_delete_view, name='admin_scholarship_delete'),
    path('adminpanel/scholarships/<int:pk>/toggle/', views.admin_scholarship_toggle_view, name='admin_scholarship_toggle'),

    # Resources
    path('adminpanel/resources/', views.admin_resources_view, name='admin_resources'),
    path('adminpanel/resources/<int:pk>/delete/', views.admin_resource_delete_view, name='admin_resource_delete'),

    # SOS Monitoring
    path('adminpanel/sos/', views.admin_sos_view, name='admin_sos'),
    path('adminpanel/sos/<int:pk>/resolve/', views.admin_resolve_sos_view, name='admin_resolve_sos'),
    path('adminpanel/sos/<int:pk>/detail/', views.admin_sos_detail_view, name='admin_sos_detail'),

    # Reports
    path('adminpanel/reports/', views.admin_reports_view, name='admin_reports'),
    path('adminpanel/reports/export/', views.admin_export_report_view, name='admin_export_report'),
]
