from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import User, Education, Skill

@login_required
def profile_view(request):
    user = request.user
    # Calculate profile completion percentage
    fields = [user.first_name, user.last_name, user.email, user.phone, user.bio, user.city, user.profile_photo, user.resume]
    filled_fields = sum(1 for f in fields if f)
    profile_completion = int((filled_fields / len(fields)) * 100) if fields else 0

    # Fetch stats
    sessions_booked = user.sessions.count()
    jobs_applied = user.job_applications.count()
    schol_applied = 0
    resources_saved = 0
    
    base_layout = 'layouts/admin_layout.html' if (user.is_staff or user.role == 'admin') else 'layouts/dashboard_layout.html'
    
    return render(request, 'profile/profile.html', {
        'user': user,
        'education': user.educations.all(),
        'skills': user.skills.all(),
        'profile_completion': profile_completion,
        'sessions_booked': sessions_booked,
        'jobs_applied': jobs_applied,
        'schol_applied': schol_applied,
        'resources_saved': resources_saved,
        'base_layout': base_layout,
    })


@login_required
def profile_edit_view(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name).strip()
        user.last_name  = request.POST.get('last_name', user.last_name).strip()
        user.email      = request.POST.get('email', user.email).strip()
        user.phone      = request.POST.get('phone', user.phone).strip()
        user.bio        = request.POST.get('bio', user.bio).strip()
        user.city       = request.POST.get('city', user.city).strip()
        
        dob = request.POST.get('dob')
        if dob:
            user.dob = dob
            
        if 'profile_photo' in request.FILES:
            user.profile_photo = request.FILES['profile_photo']
            
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    base_layout = 'layouts/admin_layout.html' if (user.is_staff or user.role == 'admin') else 'layouts/dashboard_layout.html'
    return render(request, 'profile/profile.html', {
        'user': user,
        'base_layout': base_layout,
    })


@login_required
def add_education_view(request):
    if request.method == 'POST':
        degree = request.POST.get('degree', '').strip()
        institution = request.POST.get('institution', '').strip()
        start_year = request.POST.get('start_year', '0')
        end_year = request.POST.get('end_year')
        grade = request.POST.get('grade', '').strip()

        try:
            start_year = int(start_year) if start_year.isdigit() else 0
        except ValueError:
            start_year = 0

        try:
            end_year = int(end_year) if end_year and end_year.isdigit() else None
        except ValueError:
            end_year = None

        Education.objects.create(
            user=request.user,
            degree=degree,
            institution=institution,
            year_start=start_year,
            year_end=end_year,
            grade=grade,
        )
        messages.success(request, 'Education added successfully!')
    return redirect('profile')


@login_required
def upload_resume_view(request):
    if request.method == 'POST' and 'resume' in request.FILES:
        request.user.resume = request.FILES['resume']
        request.user.save()
        messages.success(request, 'Resume uploaded successfully!')
    return redirect('profile')


@login_required
def add_skill_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            Skill.objects.get_or_create(user=request.user, name=name)
            messages.success(request, 'Skill added successfully!')
    return redirect('profile')


@login_required
def delete_skill_view(request, pk):
    skill = get_object_or_404(Skill, pk=pk, user=request.user)
    skill.delete()
    messages.success(request, 'Skill removed successfully!')
    return redirect('profile')
