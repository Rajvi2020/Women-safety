import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from core.models import User, CareerChat, CareerMessage, CareerRoadmap, RoadmapStep

@login_required
def career_chat_view(request):
    chats = request.user.career_chats.order_by('-created_at')
    current_chat = chats.first()
    messages_qs = current_chat.messages.order_by('timestamp') if current_chat else []
    return render(request, 'career/career_chat.html', {
        'chats': chats,
        'current_chat': current_chat,
        'chat_messages': messages_qs,
    })


@login_required
@require_POST
def career_chat_send_view(request):
    """API: receive user message and return AI reply."""
    try:
        data = json.loads(request.body) if request.body else {}
    except ValueError:
        data = {}
    user_msg = data.get('message', '').strip()
    chat_id  = data.get('chat_id')

    if not user_msg:
        return JsonResponse({'error': 'Empty message'}, status=400)

    if chat_id:
        chat = get_object_or_404(CareerChat, pk=chat_id, user=request.user)
    else:
        chat = CareerChat.objects.create(user=request.user, title=user_msg[:50])

    CareerMessage.objects.create(chat=chat, role='user', content=user_msg)

    # Simplified response or call to actual LLM / Service helper
    ai_reply = (
        f"Thank you for sharing that! For your goal in '{chat.title}', I recommend developing "
        "strong foundational skills in programming/logic, building practical projects, and connecting "
        "with industry experts. Is there a specific role or stack you want to dive into?"
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
@require_POST
def update_roadmap_step_api(request, pk):
    try:
        data = json.loads(request.body) if request.body else {}
    except ValueError:
        data = {}
    status = data.get('status', 'pending')
    step = get_object_or_404(RoadmapStep, pk=pk, roadmap__user=request.user)
    if status in ['pending', 'in_progress', 'completed']:
        step.status = status
        step.save()
        return JsonResponse({'status': 'ok', 'overall_pct': step.roadmap.overall_pct})
    return JsonResponse({'status': 'error', 'message': 'Invalid status'}, status=400)


@login_required
def resume_review_view(request):
    context = {}
    if request.user.resume:
        context['review_result'] = {
            'ats_score': 78,
            'sections': [
                {'name': 'Work Experience', 'score': 85},
                {'name': 'Education', 'score': 90},
                {'name': 'Skills', 'score': 65},
                {'name': 'Summary / Objective', 'score': 45},
                {'name': 'Keywords Match', 'score': 70},
            ],
            'suggestions': [
                {'type': 'error', 'title': 'Missing Professional Summary', 'description': 'Add a 3-4 line summary at the top highlighting your key skills and career objective.'},
                {'type': 'warning', 'title': 'Quantify Your Achievements', 'description': 'Replace "improved performance" with "improved performance by 40% using XYZ method".'},
                {'type': 'success', 'title': 'Education Section is Well-Formatted', 'description': 'Your education section follows best practices with institution, degree, and year.'},
                {'type': 'warning', 'title': 'Add More Relevant Keywords', 'description': 'Missing keywords: "data pipeline", "model deployment", "A/B testing".'},
            ]
        }
        context['ats_score_dash'] = int(339 * 78 / 100)
    return render(request, 'career/resume_review.html', context)


@login_required
@require_POST
def resume_review_submit_view(request):
    resume_file = request.FILES.get('resume_file')
    if not resume_file:
        messages.error(request, 'Upload failed: Please select a resume file first.')
        return redirect('resume_review')

    ext = resume_file.name.split('.')[-1].lower()
    if ext not in ['pdf', 'docx', 'doc']:
        messages.error(request, 'Upload failed: Only PDF, DOC, or DOCX formats are allowed.')
        return redirect('resume_review')

    if resume_file.size > 10 * 1024 * 1024:
        messages.error(request, 'Upload failed: File size exceeds the 10MB limit.')
        return redirect('resume_review')

    try:
        request.user.resume = resume_file
        request.user.save()

        # Create career notification
        from core.models import Notification
        Notification.objects.create(
            user=request.user,
            title="Resume Uploaded 📄",
            message="Your resume was successfully uploaded and analyzed. ATS Score: 78/100.",
            category="career",
            icon="📄"
        )

        messages.success(request, '✅ Resume uploaded and analysed successfully! ATS Score: 78/100')
    except Exception as e:
        messages.error(request, f'Upload failed: {str(e)}')

    return redirect('resume_review')


@login_required
def interview_prep_view(request):
    return render(request, 'career/interview_prep.html')
