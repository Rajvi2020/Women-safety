def notifications_processor(request):
    if request.user.is_authenticated:
        recent = request.user.notifications.all().order_by('-created_at')[:5]
        unread = request.user.notifications.filter(is_read=False).count()
        return {
            'recent_notifications': recent,
            'unread_notifications_count': unread,
        }
    return {
        'recent_notifications': [],
        'unread_notifications_count': 0,
    }
