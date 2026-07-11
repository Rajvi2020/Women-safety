from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.models import User, EmergencyContact, Mentor, Job, Scholarship, Notification

def get_unread_count(user):
    return user.notifications.filter(is_read=False).count() if user.is_authenticated else 0

@login_required
def dashboard_view(request):
    user = request.user
    if user.is_staff or user.role == 'admin':
        return redirect('admin_dashboard')
    elif user.role == 'mentor':
        return redirect('mentorship_requests')

    context = {
        'user': user,
        'emergency_contacts': user.emergency_contacts.all()[:3],
        'unread_count': get_unread_count(user),
        'notifications': user.notifications.order_by('-created_at')[:5],
        'mentor_count': Mentor.objects.filter(is_verified=True).count(),
        'job_count': Job.objects.filter(is_active=True).count(),
        'scholarship_count': Scholarship.objects.filter(is_active=True).count(),
        'sessions': user.sessions.filter(status='confirmed').count(),
        'sos_count': user.sos_alerts.count(),
    }
    return render(request, 'dashboard/dashboard.html', context)
