import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from core.models import User, EmergencyContact, SOSAlert, LiveLocation, VerifiedService, SafeRoute

@login_required
def sos_view(request):
    user = request.user
    return render(request, 'safety/sos.html', {
        'emergency_contacts': user.emergency_contacts.all(),
        'recent_sos': user.sos_alerts.order_by('-created_at')[:5],
        'emergency_services': VerifiedService.objects.all(),
        'safety_score': getattr(user, 'safety_score', 95),
    })

@login_required
@require_POST
def sos_trigger_view(request):
    """API endpoint: trigger an SOS alert (called via JavaScript)."""
    try:
        data = json.loads(request.body) if request.body else {}
    except ValueError:
        data = {}
    alert = SOSAlert.objects.create(
        user=request.user,
        latitude=data.get('lat'),
        longitude=data.get('lng'),
        location=data.get('location', ''),
        status='active',
    )
    # Create notification
    from core.models import Notification
    Notification.objects.create(
        user=request.user,
        title="SOS Alert Activated 🚨",
        message=f"SOS triggered at {data.get('location', 'current location')}. Emergency contacts notified.",
        category="safety",
        icon="🚨"
    )
    return JsonResponse({'status': 'ok', 'id': alert.id})

@login_required
def emergency_contacts_view(request):
    return render(request, 'safety/sos.html', {
        'emergency_contacts': request.user.emergency_contacts.all(),
    })

@login_required
def add_contact_view(request):
    if request.method == 'POST':
        relation = request.POST.get('relation', 'other').strip().lower()
        if relation == 'husband':
            relation = 'spouse'
        EmergencyContact.objects.create(
            user=request.user,
            name=request.POST.get('name', '').strip(),
            phone=request.POST.get('phone', '').strip(),
            relation=relation if relation in dict(EmergencyContact.RELATION_CHOICES) else 'other',
        )
        messages.success(request, 'Emergency contact added!')
    return redirect('sos')

@login_required
def delete_contact_view(request, pk):
    contact = get_object_or_404(EmergencyContact, pk=pk, user=request.user)
    contact.delete()
    messages.success(request, 'Contact removed.')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.method == 'DELETE':
        return JsonResponse({'status': 'ok'})
    return redirect('sos')

@login_required
def live_location_view(request):
    return render(request, 'safety/live_location.html', {
        'shared_contacts': request.user.emergency_contacts.all(),
        'shared_with_count': request.user.emergency_contacts.count(),
    })

@login_required
@require_POST
def update_location_api(request):
    try:
        data = json.loads(request.body) if request.body else {}
    except ValueError:
        data = {}
    lat = data.get('lat')
    lng = data.get('lng')
    loc_name = data.get('location', '')
    if lat is not None and lng is not None:
        LiveLocation.objects.create(
            user=request.user,
            latitude=lat,
            longitude=lng,
            location_name=loc_name
        )
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error', 'message': 'Missing coordinates'}, status=400)

@login_required
def safe_route_view(request):
    if request.method == 'POST':
        start = request.POST.get('from', '').strip()
        end = request.POST.get('to', '').strip()
        mode = request.POST.get('mode', 'walk').strip()
        if start and end:
            SafeRoute.objects.create(
                user=request.user,
                start_location=start,
                end_location=end,
                travel_mode=mode
            )
            from core.models import Notification
            Notification.objects.create(
                user=request.user,
                title="Safe Route Planned 🗺️",
                message=f"Planned {mode} route from {start} to {end} successfully.",
                category="safety",
                icon="🗺️"
            )
            messages.success(request, 'Route planned successfully!')
    return render(request, 'safety/safe_route.html', {
        'current_location': request.GET.get('from', ''),
    })
