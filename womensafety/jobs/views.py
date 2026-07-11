from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from core.models import User, Job, JobApplication, SavedJob

@login_required
def job_list_view(request):
    jobs = Job.objects.filter(is_active=True)
    
    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    location = request.GET.get('location', '').strip()
    job_type = request.GET.get('type', '').strip()

    if q:
        jobs = jobs.filter(title__icontains=q) | jobs.filter(company__icontains=q)
    if category:
        jobs = jobs.filter(category__iexact=category)
    if location:
        if location.lower() == 'remote':
            jobs = jobs.filter(location__icontains='remote')
        else:
            jobs = jobs.filter(location__icontains=location)
    if job_type:
        jobs = jobs.filter(type__iexact=job_type)

    saved_job_ids = SavedJob.objects.filter(user=request.user).values_list('job_id', flat=True)

    return render(request, 'jobs/job_list.html', {
        'jobs': jobs,
        'total_jobs': Job.objects.filter(is_active=True).count(),
        'applied_count': request.user.job_applications.count(),
        'saved_job_ids': list(saved_job_ids),
    })


@login_required
def job_detail_view(request, pk):
    job = get_object_or_404(Job, pk=pk)
    applied = JobApplication.objects.filter(user=request.user, job=job).exists()
    saved = SavedJob.objects.filter(user=request.user, job=job).exists()
    similar_jobs = Job.objects.filter(category=job.category, is_active=True).exclude(pk=pk)[:3]
    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'applied': applied,
        'saved': saved,
        'similar_jobs': similar_jobs,
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


@login_required
def saved_jobs_view(request):
    saved = SavedJob.objects.filter(user=request.user).select_related('job')
    return render(request, 'jobs/saved_jobs.html', {'saved_jobs': saved})


@login_required
@require_POST
def toggle_save_job_api(request, pk):
    job = get_object_or_404(Job, pk=pk)
    saved_job, created = SavedJob.objects.get_or_create(user=request.user, job=job)
    if not created:
        return JsonResponse({'status': 'already_saved'})
        
    # Create notification
    from core.models import Notification
    Notification.objects.create(
        user=request.user,
        title="Job Saved 💼",
        message=f"You successfully saved the job post: {job.title} at {job.company}.",
        category="career",
        icon="💼"
    )
    return JsonResponse({'status': 'saved'})
