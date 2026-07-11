from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from core.models import User, Mentor, MentorSession

@login_required
def mentor_list_view(request):
    mentors = Mentor.objects.filter(is_verified=True).select_related('user')
    q = request.GET.get('q', '')
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

    if not date:
        messages.error(request, 'Please select a date for the session.')
        return redirect('mentor_detail', pk=mentor.id)

    MentorSession.objects.create(
        user=request.user,
        mentor=mentor,
        session_type=session_type,
        date=date,
        time_slot=time_slot,
        notes=notes,
        status='pending'
    )
    messages.success(request, f'Session booked with {mentor.user.get_full_name()}! 🎉')
    return redirect('mentors')


@login_required
def mentorship_requests_view(request):
    """View to list bookings requested of the current user if they are a mentor."""
    try:
        mentor = request.user.mentor_profile
    except Mentor.DoesNotExist:
        messages.error(request, "Only mentors can access mentorship requests.")
        return redirect('dashboard')
    
    sessions = mentor.sessions.all().order_by('-date')
    return render(request, 'mentors/requests.html', {'sessions': sessions})


@login_required
def update_session_status_view(request, pk, status):
    """Approve/Reject/Cancel a session request."""
    session = get_object_or_404(MentorSession, pk=pk)
    if session.mentor.user != request.user and session.user != request.user:
        messages.error(request, "You are not authorized to update this session.")
        return redirect('dashboard')
        
    if status in ['confirmed', 'completed', 'cancelled']:
        session.status = status
        session.save()
        messages.success(request, f"Session status updated to {status}!")
        
    if session.mentor.user == request.user:
        return redirect('mentorship_requests')
    return redirect('dashboard')
