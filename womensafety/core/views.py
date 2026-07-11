"""
SheShield AI — Core App Views
All view functions for the application.
"""
import json
import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import (
    User, Education, Skill, EmergencyContact, SOSAlert,
    Mentor, MentorSkill, MentorSession, MentorReview,
    Job, JobApplication, SavedJob, Scholarship, Resource,
    FAQ, Notification, CareerChat, CareerMessage,
    CareerRoadmap, RoadmapStep,
)


# ─────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.role == 'admin')


def get_unread_count(user):
    return user.notifications.filter(is_read=False).count() if user.is_authenticated else 0


# ─────────────────────────────────────────────────────────────────
# Auth Views
# ─────────────────────────────────────────────────────────────────

def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        email      = request.POST.get('email', '').strip()
        phone      = request.POST.get('phone', '').strip()
        password   = request.POST.get('password', '')
        confirm    = request.POST.get('confirm_password', '')

        if password != confirm:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
        elif len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        else:
            user = User.objects.create_user(
                username=email, email=email, password=password,
                first_name=first_name, last_name=last_name, phone=phone,
            )
            login(request, user)
            messages.success(request, f'Welcome to SheShield AI, {first_name}! 🎉')
            return redirect('dashboard')
    return render(request, 'auth/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        email    = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user is None:
            # Try authenticating by email field
            try:
                u = User.objects.get(email=email)
                user = authenticate(request, username=u.username, password=password)
            except User.DoesNotExist:
                user = None
        if user:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        messages.error(request, 'Invalid email or password.')
    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def forgot_password_view(request):
    return render(request, 'auth/forgot_password.html')


def reset_password_view(request):
    return render(request, 'auth/forgot_password.html')


# ─────────────────────────────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────────────────────────────

@login_required
def dashboard_view(request):
    user = request.user
    context = {
        'user': user,
        'emergency_contacts': user.emergency_contacts.all()[:3],
        'unread_count': get_unread_count(user),
        'notifications': user.notifications.all()[:5],
        'mentor_count': Mentor.objects.filter(is_verified=True).count(),
        'job_count': Job.objects.filter(is_active=True).count(),
        'scholarship_count': Scholarship.objects.filter(is_active=True).count(),
        'sessions': user.sessions.filter(status='confirmed').count(),
        'sos_count': user.sos_alerts.count(),
    }
    return render(request, 'dashboard/dashboard.html', context)


# ─────────────────────────────────────────────────────────────────
# Profile
# ─────────────────────────────────────────────────────────────────

@login_required
def profile_view(request):
    user = request.user
    return render(request, 'profile/profile.html', {
        'user': user,
        'educations': user.educations.all(),
        'skills': user.skills.all(),
    })


@login_required
def profile_edit_view(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name  = request.POST.get('last_name', user.last_name)
        user.phone      = request.POST.get('phone', user.phone)
        user.bio        = request.POST.get('bio', user.bio)
        user.city       = request.POST.get('city', user.city)
        if 'profile_photo' in request.FILES:
            user.profile_photo = request.FILES['profile_photo']
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    return render(request, 'profile/profile.html', {'user': user})


@login_required
def add_education_view(request):
    if request.method == 'POST':
        Education.objects.create(
            user=request.user,
            degree=request.POST.get('degree', ''),
            institution=request.POST.get('institution', ''),
            year_start=request.POST.get('year_start', 0),
            year_end=request.POST.get('year_end') or None,
            grade=request.POST.get('grade', ''),
        )
        messages.success(request, 'Education added!')
    return redirect('profile')


@login_required
def upload_resume_view(request):
    if request.method == 'POST' and 'resume' in request.FILES:
        request.user.resume = request.FILES['resume']
        request.user.save()
        messages.success(request, 'Resume uploaded!')
    return redirect('profile')


# ─────────────────────────────────────────────────────────────────
# Safety
# ─────────────────────────────────────────────────────────────────

@login_required
def sos_view(request):
    user = request.user
    return render(request, 'safety/sos.html', {
        'contacts': user.emergency_contacts.all(),
        'recent_sos': user.sos_alerts.order_by('-created_at')[:5],
        'safety_score': user.safety_score,
    })


@login_required
@require_POST
def sos_trigger_view(request):
    """API endpoint: trigger an SOS alert (called via JavaScript)."""
    data = json.loads(request.body) if request.body else {}
    alert = SOSAlert.objects.create(
        user=request.user,
        latitude=data.get('lat'),
        longitude=data.get('lng'),
        location=data.get('location', ''),
        status='active',
    )
    # TODO: Send SMS/email to emergency contacts
    return JsonResponse({'status': 'ok', 'id': alert.id})


@login_required
def emergency_contacts_view(request):
    return render(request, 'safety/sos.html', {
        'contacts': request.user.emergency_contacts.all(),
    })


@login_required
def add_contact_view(request):
    if request.method == 'POST':
        EmergencyContact.objects.create(
            user=request.user,
            name=request.POST.get('name', ''),
            phone=request.POST.get('phone', ''),
            relation=request.POST.get('relation', 'other'),
        )
        messages.success(request, 'Emergency contact added!')
    return redirect('sos')


@login_required
def delete_contact_view(request, pk):
    contact = get_object_or_404(EmergencyContact, pk=pk, user=request.user)
    contact.delete()
    messages.success(request, 'Contact removed.')
    return redirect('sos')


@login_required
def live_location_view(request):
    return render(request, 'safety/live_location.html', {
        'shared_contacts': request.user.emergency_contacts.all(),
        'shared_with_count': request.user.emergency_contacts.count(),
    })


@login_required
def safe_route_view(request):
    return render(request, 'safety/safe_route.html', {
        'current_location': request.GET.get('from', ''),
    })


# ─────────────────────────────────────────────────────────────────
# Career
# ─────────────────────────────────────────────────────────────────

@login_required
def career_chat_view(request):
    chats = request.user.career_chats.order_by('-created_at')
    current_chat = chats.first()
    messages_qs = current_chat.messages.all() if current_chat else []
    return render(request, 'career/career_chat.html', {
        'chats': chats,
        'current_chat': current_chat,
        'chat_messages': messages_qs,
    })


@login_required
@require_POST
def career_chat_send_view(request):
    """API: receive user message and return AI reply."""
    data = json.loads(request.body) if request.body else {}
    user_msg = data.get('message', '').strip()
    chat_id  = data.get('chat_id')

    if not user_msg:
        return JsonResponse({'error': 'Empty message'}, status=400)

    # Get or create chat
    if chat_id:
        chat = get_object_or_404(CareerChat, pk=chat_id, user=request.user)
    else:
        chat = CareerChat.objects.create(user=request.user, title=user_msg[:50])

    CareerMessage.objects.create(chat=chat, role='user', content=user_msg)

    # Placeholder AI response — replace with real LLM call
    ai_reply = (
        "That's a great question! Based on your profile, I recommend focusing on "
        "building practical projects and contributing to open-source repositories. "
        "Would you like me to create a personalized action plan?"
    )
    CareerMessage.objects.create(chat=chat, role='ai', content=ai_reply)

    return JsonResponse({'reply': ai_reply, 'chat_id': chat.id})


@login_required
def career_roadmap_view(request):
    roadmap = getattr(request.user, 'roadmap', None)
    steps = roadmap.steps.all() if roadmap else []
    return render(request, 'career/career_roadmap.html', {
        'roadmap': roadmap,
        'roadmap_steps': steps,
        'overall_pct': roadmap.overall_pct if roadmap else 0,
        'completed': steps.filter(status='completed').count() if steps else 0,
        'in_progress': steps.filter(status='in_progress').count() if steps else 0,
        'pending': steps.filter(status='pending').count() if steps else 0,
    })


@login_required
def resume_review_view(request):
    return render(request, 'career/resume_review.html')


@login_required
@require_POST
def resume_review_submit_view(request):
    resume_file = request.FILES.get('resume_file')
    if resume_file:
        # Save file
        request.user.resume = resume_file
        request.user.save()
        # Placeholder: return mock review result
        messages.success(request, '✅ Resume analysed! ATS Score: 78/100')
    return redirect('resume_review')


@login_required
def interview_prep_view(request):
    return render(request, 'career/interview_prep.html')


# ─────────────────────────────────────────────────────────────────
# Mentors
# ─────────────────────────────────────────────────────────────────

@login_required
def mentor_list_view(request):
    mentors = Mentor.objects.filter(is_verified=True).select_related('user')
    q = request.GET.get('q', '')
    field = request.GET.get('field', '')
    if q:
        mentors = mentors.filter(user__first_name__icontains=q) | mentors.filter(title__icontains=q)
    return render(request, 'mentors/mentor_list.html', {'mentors': mentors})


@login_required
def mentor_detail_view(request, pk):
    mentor = get_object_or_404(Mentor, pk=pk)
    return render(request, 'mentors/mentor_detail.html', {'mentor': mentor})


@login_required
@require_POST
def book_session_view(request):
    mentor_id   = request.POST.get('mentor_id')
    mentor      = get_object_or_404(Mentor, pk=mentor_id)
    session_type = request.POST.get('session_type', 'video')
    date        = request.POST.get('date')
    time_slot   = request.POST.get('time_slot', '')
    notes       = request.POST.get('notes', '')

    MentorSession.objects.create(
        user=request.user,
        mentor=mentor,
        session_type=session_type,
        date=date,
        time_slot=time_slot,
        notes=notes,
    )
    messages.success(request, f'Session booked with {mentor.user.get_full_name()}! 🎉')
    return redirect('mentors')


# ─────────────────────────────────────────────────────────────────
# Jobs
# ─────────────────────────────────────────────────────────────────

@login_required
def job_list_view(request):
    jobs = Job.objects.filter(is_active=True)
    q = request.GET.get('q', '')
    if q:
        jobs = jobs.filter(title__icontains=q) | jobs.filter(company__icontains=q)
    return render(request, 'jobs/job_list.html', {
        'jobs': jobs,
        'total_jobs': Job.objects.filter(is_active=True).count(),
        'applied_count': request.user.job_applications.count(),
    })


@login_required
def job_detail_view(request, pk):
    job = get_object_or_404(Job, pk=pk)
    applied = JobApplication.objects.filter(user=request.user, job=job).exists()
    similar_jobs = Job.objects.filter(category=job.category, is_active=True).exclude(pk=pk)[:3]
    return render(request, 'jobs/job_detail.html', {
        'job': job, 'applied': applied, 'similar_jobs': similar_jobs,
    })


@login_required
def apply_job_view(request, pk):
    job = get_object_or_404(Job, pk=pk)
    _, created = JobApplication.objects.get_or_create(user=request.user, job=job)
    if created:
        job.applicants += 1
        job.save(update_fields=['applicants'])
        messages.success(request, f'Applied to {job.title} successfully! ✅')
    else:
        messages.info(request, 'You have already applied to this job.')
    return redirect('job_detail', pk=pk)


# ─────────────────────────────────────────────────────────────────
# Scholarships
# ─────────────────────────────────────────────────────────────────

@login_required
def scholarship_list_view(request):
    scholarships = Scholarship.objects.filter(is_active=True)
    return render(request, 'scholarships/scholarship_list.html', {'scholarships': scholarships})


@login_required
def scholarship_detail_view(request, pk):
    scholarship = get_object_or_404(Scholarship, pk=pk)
    return render(request, 'scholarships/scholarship_list.html', {'scholarship': scholarship})


# ─────────────────────────────────────────────────────────────────
# Resources
# ─────────────────────────────────────────────────────────────────

@login_required
def resources_view(request):
    return render(request, 'resources/resources.html', {
        'faqs': FAQ.objects.all(),
        'resources': Resource.objects.all(),
    })


# ─────────────────────────────────────────────────────────────────
# Notifications
# ─────────────────────────────────────────────────────────────────

@login_required
def notifications_view(request):
    notifs = request.user.notifications.all()
    return render(request, 'notifications/notifications.html', {
        'notifications': notifs,
        'unread_count': notifs.filter(is_read=False).count(),
    })


@login_required
@require_POST
def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.is_read = True
    notif.save(update_fields=['is_read'])
    return JsonResponse({'status': 'ok'})


# ─────────────────────────────────────────────────────────────────
# Settings
# ─────────────────────────────────────────────────────────────────

@login_required
def settings_view(request):
    return render(request, 'settings/settings.html')


@login_required
@require_POST
def change_password_view(request):
    current  = request.POST.get('current_password', '')
    new_pwd  = request.POST.get('new_password', '')
    confirm  = request.POST.get('confirm_password', '')
    user = request.user
    if not user.check_password(current):
        messages.error(request, 'Current password is incorrect.')
    elif new_pwd != confirm:
        messages.error(request, 'New passwords do not match.')
    elif len(new_pwd) < 8:
        messages.error(request, 'Password must be at least 8 characters.')
    else:
        user.set_password(new_pwd)
        user.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Password updated successfully!')
    return redirect('settings')


@login_required
def delete_account_view(request):
    request.user.delete()
    logout(request)
    messages.success(request, 'Your account has been deleted.')
    return redirect('login')


# ─────────────────────────────────────────────────────────────────
# Admin Views (staff only)
# ─────────────────────────────────────────────────────────────────

@login_required
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    return render(request, 'admin/admin_dashboard.html', {
        'total_users': User.objects.count(),
        'total_mentors': Mentor.objects.filter(is_verified=True).count(),
        'pending_mentors': Mentor.objects.filter(is_verified=False).count(),
        'pending_mentors_list': Mentor.objects.filter(is_verified=False).select_related('user')[:5],
        'active_jobs': Job.objects.filter(is_active=True).count(),
        'sos_today': SOSAlert.objects.filter(created_at__date=timezone.now().date()).count(),
        'sos_resolved': SOSAlert.objects.filter(created_at__date=timezone.now().date(), status='resolved').count(),
        'recent_users': User.objects.order_by('-date_joined')[:5],
        'recent_sos': SOSAlert.objects.order_by('-created_at')[:5],
        'pending_count': Mentor.objects.filter(is_verified=False).count(),
    })


@login_required
@user_passes_test(is_admin)
def admin_users_view(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'admin/admin_users.html', {
        'users': users,
        'total': users.count(),
    })


@login_required
@user_passes_test(is_admin)
def admin_user_detail_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'admin/admin_users.html', {'selected_user': user})


@login_required
@user_passes_test(is_admin)
def admin_export_users_view(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sheshield_users.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Role', 'Joined', 'Active'])
    for user in User.objects.all():
        writer.writerow([user.pk, user.get_full_name(), user.email,
                         user.phone, user.role, user.date_joined.strftime('%d %b %Y'), user.is_active])
    return response


@login_required
@user_passes_test(is_admin)
def admin_mentors_view(request):
    pending = Mentor.objects.filter(is_verified=False).select_related('user')
    approved = Mentor.objects.filter(is_verified=True).select_related('user')
    return render(request, 'admin/admin_dashboard.html', {
        'pending_mentors_list': pending,
        'approved_mentors': approved,
    })


@login_required
@user_passes_test(is_admin)
@require_POST
def admin_approve_mentor_view(request, pk):
    mentor = get_object_or_404(Mentor, pk=pk)
    mentor.is_verified = True
    mentor.save(update_fields=['is_verified'])
    return JsonResponse({'status': 'approved'})


@login_required
@user_passes_test(is_admin)
@require_POST
def admin_reject_mentor_view(request, pk):
    mentor = get_object_or_404(Mentor, pk=pk)
    mentor.delete()
    return JsonResponse({'status': 'rejected'})


@login_required
@user_passes_test(is_admin)
def admin_jobs_view(request):
    if request.method == 'POST':
        Job.objects.create(
            title=request.POST.get('title', ''),
            company=request.POST.get('company', ''),
            location=request.POST.get('location', ''),
            salary=request.POST.get('salary', ''),
            description=request.POST.get('description', ''),
            category=request.POST.get('category', ''),
            type=request.POST.get('type', 'full-time'),
            is_women_friendly='is_women_friendly' in request.POST,
        )
        messages.success(request, 'Job posted successfully!')
    jobs = Job.objects.all().order_by('-posted_at')
    return render(request, 'admin/admin_jobs.html', {'jobs': jobs})


@login_required
@user_passes_test(is_admin)
def admin_scholarships_view(request):
    return render(request, 'admin/admin_dashboard.html', {
        'scholarships': Scholarship.objects.all(),
    })


@login_required
@user_passes_test(is_admin)
def admin_resources_view(request):
    return render(request, 'admin/admin_dashboard.html', {
        'resources': Resource.objects.all(),
    })


@login_required
@user_passes_test(is_admin)
def admin_sos_view(request):
    active = SOSAlert.objects.filter(status='active').select_related('user')
    history = SOSAlert.objects.order_by('-created_at').select_related('user')[:50]
    return render(request, 'admin/admin_sos.html', {
        'active_sos': active,
        'active_sos_count': active.count(),
        'active_now': active.count(),
        'sos_history': history,
        'total_today': SOSAlert.objects.filter(created_at__date=timezone.now().date()).count(),
        'resolved_today': SOSAlert.objects.filter(created_at__date=timezone.now().date(), status='resolved').count(),
    })


@login_required
@user_passes_test(is_admin)
@require_POST
def admin_resolve_sos_view(request, pk):
    alert = get_object_or_404(SOSAlert, pk=pk)
    alert.status = 'resolved'
    alert.resolved_at = timezone.now()
    alert.save(update_fields=['status', 'resolved_at'])
    return JsonResponse({'status': 'resolved'})


@login_required
@user_passes_test(is_admin)
def admin_reports_view(request):
    return render(request, 'admin/admin_reports.html', {
        'new_users': User.objects.count(),
        'sessions': MentorSession.objects.count(),
        'applied': JobApplication.objects.count(),
        'sos_total': SOSAlert.objects.count(),
    })
