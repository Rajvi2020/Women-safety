from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_redirect, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path('settings/', views.settings_view, name='settings'),
    path('settings/password/', views.change_password_view, name='change_password'),
    path('settings/delete-account/', views.delete_account_view, name='delete_account'),
    path('google-login/', views.google_login_view, name='google_login'),
]
