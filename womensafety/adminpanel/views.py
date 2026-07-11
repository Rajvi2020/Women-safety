import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_POST, require_http_methods
from django.db.models import Count
from core.models import User, Mentor, Job, SOSAlert, Scholarship, Resource, MentorSession, JobApplication


def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.role == 'admin')


# ─── Dashboard ───────────────────────────────────────────────────────────────
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
        'sessions': MentorSession.objects.count(),
        'applications': JobApplication.objects.count(),
    })


# ─── User Management ─────────────────────────────────────────────────────────
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
    return render(request, 'admin/admin_users.html', {
        'users': User.objects.all().order_by('-date_joined'),
        'total': User.objects.count(),
        'selected_user': user,
    })


@login_required
@user_passes_test(is_admin)
@require_POST
def admin_user_delete_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        return JsonResponse({'status': 'error', 'message': 'Cannot delete your own account'}, status=400)
    name = user.get_full_name() or user.email
    user.delete()
    return JsonResponse({'status': 'deleted', 'message': f'User "{name}" deleted successfully'})


@login_required
@user_passes_test(is_admin)
@require_POST
def admin_user_toggle_active_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])
    status = 'activated' if user.is_active else 'deactivated'
    return JsonResponse({'status': status, 'is_active': user.is_active})


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


# ─── Mentor Management ───────────────────────────────────────────────────────
@login_required
@user_passes_test(is_admin)
def admin_mentors_view(request):
    pending = Mentor.objects.filter(is_verified=False).select_related('user')
    approved = Mentor.objects.filter(is_verified=True).select_related('user')
    return render(request, 'admin/admin_mentors.html', {
        'pending_mentors_list': pending,
        'approved_mentors': approved,
        'pending_count': pending.count(),
        'approved_count': approved.count(),
    })


@login_required
@user_passes_test(is_admin)
@require_POST
def admin_approve_mentor_view(request, pk):
    mentor = get_object_or_404(Mentor, pk=pk)
    mentor.is_verified = True
    mentor.save(update_fields=['is_verified'])
    # Notify the mentor user
    from core.models import Notification
    Notification.objects.create(
        user=mentor.user,
        title='Mentor Application Approved! 🎉',
        message='Congratulations! Your mentor application has been approved. You can now appear in mentor listings.',
        type='success'
    )
    return JsonResponse({'status': 'approved', 'message': f'{mentor.user.get_full_name()} approved as mentor'})


@login_required
@user_passes_test(is_admin)
@require_POST
def admin_reject_mentor_view(request, pk):
    mentor = get_object_or_404(Mentor, pk=pk)
    name = mentor.user.get_full_name()
    mentor.delete()
    return JsonResponse({'status': 'rejected', 'message': f'Mentor application for {name} rejected'})


# ─── Job Management ──────────────────────────────────────────────────────────
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
            category=request.POST.get('category', 'Technology'),
            type=request.POST.get('type', 'full-time'),
            is_women_friendly='is_women_friendly' in request.POST,
            is_active=True,
        )
        messages.success(request, 'Job posted successfully!')
        return redirect('admin_jobs')
    jobs = Job.objects.all().order_by('-posted_at')
    return render(request, 'admin/admin_jobs.html', {'jobs': jobs})


@login_required
@user_passes_test(is_admin)
def admin_job_edit_view(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.method == 'POST':
        job.title = request.POST.get('title', job.title)
        job.company = request.POST.get('company', job.company)
        job.location = request.POST.get('location', job.location)
        job.salary = request.POST.get('salary', job.salary)
        job.description = request.POST.get('description', job.description)
        job.category = request.POST.get('category', job.category)
        job.type = request.POST.get('type', job.type)
        job.is_women_friendly = 'is_women_friendly' in request.POST
        job.is_active = 'is_active' in request.POST
        job.save()
        return JsonResponse({'status': 'updated', 'message': f'Job "{job.title}" updated successfully'})
    # GET – return job data as JSON for modal
    return JsonResponse({
        'id': job.id,
        'title': job.title,
        'company': job.company,
        'location': job.location,
        'salary': job.salary,
        'description': job.description,
        'category': job.category,
        'type': job.type,
        'is_women_friendly': job.is_women_friendly,
        'is_active': job.is_active,
    })


@login_required
@user_passes_test(is_admin)
@require_POST
def admin_job_delete_view(request, pk):
    job = get_object_or_404(Job, pk=pk)
    title = job.title
    job.delete()
    return JsonResponse({'status': 'deleted', 'message': f'Job "{title}" deleted successfully'})


# ─── Scholarship Management ──────────────────────────────────────────────────
@login_required
@user_passes_test(is_admin)
def admin_scholarships_view(request):
    if request.method == 'POST':
        try:
            from datetime import date
            deadline_str = request.POST.get('deadline', '')
            deadline = date.fromisoformat(deadline_str) if deadline_str else timezone.now().date()
            Scholarship.objects.create(
                name=request.POST.get('name', ''),
                provider=request.POST.get('provider', ''),
                description=request.POST.get('description', ''),
                amount=request.POST.get('amount', ''),
                category=request.POST.get('category', 'General'),
                level=request.POST.get('level', 'Undergraduate'),
                deadline=deadline,
                icon=request.POST.get('icon', '🎓'),
                apply_url=request.POST.get('apply_url', ''),
                is_active=True,
            )
            messages.success(request, 'Scholarship added successfully!')
        except Exception as e:
            messages.error(request, f'Error adding scholarship: {e}')
        return redirect('admin_scholarships')
    scholarships = Scholarship.objects.all().order_by('deadline')
    return render(request, 'admin/admin_scholarships.html', {'scholarships': scholarships})


@login_required
@user_passes_test(is_admin)
@require_POST
def admin_scholarship_delete_view(request, pk):
    scholarship = get_object_or_404(Scholarship, pk=pk)
    name = scholarship.name
    scholarship.delete()
    return JsonResponse({'status': 'deleted', 'message': f'Scholarship "{name}" deleted successfully'})


@login_required
@user_passes_test(is_admin)
def admin_scholarship_toggle_view(request, pk):
    scholarship = get_object_or_404(Scholarship, pk=pk)
    scholarship.is_active = not scholarship.is_active
    scholarship.save(update_fields=['is_active'])
    return JsonResponse({'status': 'ok', 'is_active': scholarship.is_active})


# ─── Resources ───────────────────────────────────────────────────────────────
@login_required
@user_passes_test(is_admin)
def admin_resources_view(request):
    if request.method == 'POST':
        Resource.objects.create(
            title=request.POST.get('title', ''),
            description=request.POST.get('description', ''),
            category=request.POST.get('category', 'other'),
            url=request.POST.get('url', ''),
        )
        messages.success(request, 'Resource added successfully!')
        return redirect('admin_resources')
    return render(request, 'admin/admin_resources.html', {
        'resources': Resource.objects.all().order_by('-created_at'),
    })


@login_required
@user_passes_test(is_admin)
@require_POST
def admin_resource_delete_view(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    title = resource.title
    resource.delete()
    return JsonResponse({'status': 'deleted', 'message': f'Resource "{title}" deleted'})


# ─── SOS Monitoring ──────────────────────────────────────────────────────────
@login_required
@user_passes_test(is_admin)
def admin_sos_view(request):
    active = SOSAlert.objects.filter(status='active').select_related('user').order_by('-created_at')
    history = SOSAlert.objects.order_by('-created_at').select_related('user')[:100]
    return render(request, 'admin/admin_sos.html', {
        'active_sos': active,
        'sos_history': history,
        'active_sos_count': active.count(),
        'active_now': active.count(),
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
    return JsonResponse({'status': 'resolved', 'message': 'SOS alert marked as resolved'})


@login_required
@user_passes_test(is_admin)
def admin_sos_detail_view(request, pk):
    sos = get_object_or_404(SOSAlert, pk=pk)
    return JsonResponse({
        'id': sos.id,
        'user': sos.user.get_full_name(),
        'phone': sos.user.phone or '—',
        'email': sos.user.email,
        'location': sos.location or '—',
        'status': sos.status,
        'created_at': sos.created_at.strftime('%d %b %Y, %H:%M'),
        'resolved_at': sos.resolved_at.strftime('%d %b %Y, %H:%M') if sos.resolved_at else '—',
    })


# ─── Reports ─────────────────────────────────────────────────────────────────
@login_required
@user_passes_test(is_admin)
def admin_reports_view(request):
    try:
        from django.db.models.functions import TruncMonth
        from datetime import timedelta
        monthly_growth = (
            User.objects
            .annotate(month=TruncMonth('date_joined'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        chart_data = [(r['month'].strftime('%b'), r['count']) for r in monthly_growth[-6:]]
    except Exception:
        chart_data = []

    return render(request, 'admin/admin_reports.html', {
        'new_users': User.objects.count(),
        'sessions': MentorSession.objects.count(),
        'applied': JobApplication.objects.count(),
        'sos_total': SOSAlert.objects.count(),
        'monthly_growth': chart_data,
    })


@login_required
@user_passes_test(is_admin)
def admin_export_report_view(request):
    """Export full platform report as CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sheshield_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Section', 'Metric', 'Value'])
    writer.writerow(['Users', 'Total', User.objects.count()])
    writer.writerow(['Users', 'Active', User.objects.filter(is_active=True).count()])
    writer.writerow(['Mentors', 'Verified', Mentor.objects.filter(is_verified=True).count()])
    writer.writerow(['Mentors', 'Pending', Mentor.objects.filter(is_verified=False).count()])
    writer.writerow(['Jobs', 'Active', Job.objects.filter(is_active=True).count()])
    writer.writerow(['Jobs', 'Total', Job.objects.count()])
    writer.writerow(['Sessions', 'Total', MentorSession.objects.count()])
    writer.writerow(['Applications', 'Total', JobApplication.objects.count()])
    writer.writerow(['SOS Alerts', 'Total', SOSAlert.objects.count()])
    writer.writerow(['SOS Alerts', 'Resolved', SOSAlert.objects.filter(status='resolved').count()])
    return response
