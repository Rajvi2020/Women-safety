from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from core.models import Notification

@login_required
def notifications_view(request):
    notifs = request.user.notifications.all().order_by('-created_at')
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


@login_required
@require_POST
def mark_all_notifications_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return JsonResponse({'status': 'ok'})
