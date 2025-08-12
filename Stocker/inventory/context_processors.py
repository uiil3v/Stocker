from .models import Notification

def unread_notifications_count(request):
    if request.user.is_authenticated:
        return {
            'notifications_unread_count': Notification.objects.filter(user=request.user, is_read=False).count()
        }
    return {'notifications_unread_count': 0}
