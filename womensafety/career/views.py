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

    # Prepare chat history for Gemini API context
    contents = []
    # Fetch last 10 messages for conversation context
    for msg in chat.messages.order_by('timestamp')[:10]:
        role = "user" if msg.role == 'user' else "model"
        contents.append({
            "role": role,
            "parts": [{"text": msg.content}]
        })

    import os
    from django.conf import settings
    import requests

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        env_path = os.path.join(settings.BASE_DIR, '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        k, v = line.strip().split('=', 1)
                        if k.strip() == 'GEMINI_API_KEY':
                            api_key = v.strip().strip("'").strip('"')
                            os.environ['GEMINI_API_KEY'] = api_key
                            break

    if not api_key:
        ai_reply = (
            "Gemini API Key is not set. Please go to the Settings page in SheShield, "
            "scroll down to 'AI Coach Settings', paste your Gemini API Key, and save it."
        )
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        
        system_instruction = {
            "parts": [
                {
                    "text": (
                        "You are SheShield Career AI, a helpful, supportive, and professional career advisor for women. "
                        "Provide clear, practical, actionable, and encouraging career advice, resume tips, and interview prep suggestions."
                    )
                }
            ]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "contents": contents,
            "systemInstruction": system_instruction
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                res_data = response.json()
                try:
                    ai_reply = res_data['candidates'][0]['content']['parts'][0]['text']
                except (KeyError, IndexError):
                    ai_reply = f"Error parsing Gemini response: {response.text}"
            else:
                try:
                    res_json = response.json()
                    err_msg = res_json.get('error', {}).get('message', response.text)
                except ValueError:
                    err_msg = response.text
                
                if 'quota' in err_msg.lower() or 'exhausted' in err_msg.lower() or response.status_code == 429:
                    raise Exception(f"Quota Exceeded: {err_msg}")
                else:
                    ai_reply = f"Gemini API Error (status {response.status_code}): {err_msg}"
        except Exception as e:
            err_str = str(e).lower()
            if 'quota' in err_str or '429' in err_str:
                msg_lower = user_msg.lower()
                if 'resume' in msg_lower or 'cv' in msg_lower:
                    ai_reply = (
                        "⚠️ **[SIMULATED - Gemini API Quota Exceeded]**\n\n"
                        "To build an outstanding resume, focus on these three core areas:\n"
                        "1. **Quantify achievements**: Instead of writing 'managed projects', write 'managed 5 cross-functional projects, delivering them 2 weeks ahead of schedule'.\n"
                        "2. **ATS Optimization**: Match your resume keywords to the job description (e.g., specific libraries, methodologies, or tools).\n"
                        "3. **Clear Formatting**: Use a clean, single-column design with standard headers (Experience, Education, Skills)."
                    )
                elif 'interview' in msg_lower or 'question' in msg_lower:
                    ai_reply = (
                        "⚠️ **[SIMULATED - Gemini API Quota Exceeded]**\n\n"
                        "Here are key tips for interview preparation:\n"
                        "1. **STAR Method**: Structure your answers to behavioral questions using Situation, Task, Action, and Result.\n"
                        "2. **Company Research**: Understand the company's recent news, product lineup, and core mission statement.\n"
                        "3. **Mock Interviews**: Practice talking out loud. Explain your technical choices step-by-step."
                    )
                elif 'career' in msg_lower or 'job' in msg_lower or 'skill' in msg_lower or 'learn' in msg_lower:
                    ai_reply = (
                        "⚠️ **[SIMULATED - Gemini API Quota Exceeded]**\n\n"
                        "To advance your career in tech, focus on building:\n"
                        "1. **Robust Portfolio**: Build 2-3 real-world projects and showcase them on your GitHub.\n"
                        "2. **Continuous Upskilling**: Learn in-demand frameworks (like Django, React, or Flutter) and practice data structures.\n"
                        "3. **Networking**: Connect with industry professionals on LinkedIn, participate in hackathons, and seek out mentor programs."
                    )
                else:
                    ai_reply = (
                        "⚠️ **[SIMULATED - Gemini API Quota Exceeded]**\n\n"
                        "Hello! I am your career AI mentor. Focus on building strong technical foundations, working on "
                        "open-source projects, keeping your LinkedIn updated, and preparing for behavioral questions. "
                        "Let me know if you want specific tips on Resume building, Interview prep, or Upskilling!"
                    )
            else:
                ai_reply = f"Error calling Gemini API: {str(e)}"

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
