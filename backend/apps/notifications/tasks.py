from datetime import timedelta
import logging

from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from django.utils import timezone

from .models import Notification
from .serializers import NotificationSerializer

logger = logging.getLogger(__name__)

@shared_task
def create_notification_task(
    user_id,
    notification_type,
    title,
    content='',
    link='',
    sender_id=None,
    related_post_id=None,
    related_comment_id=None,
):
    """Persist a notification and push it to connected clients."""
    notification = Notification.objects.create(
        user_id=user_id,
        sender_id=sender_id,
        type=notification_type,
        title=title,
        content=content,
        link=link,
        related_post_id=related_post_id,
        related_comment_id=related_comment_id,
    )
    payload = NotificationSerializer(notification).data
    try:
        async_to_sync(get_channel_layer().group_send)(
            f'user_{user_id}',
            {'type': 'notification.created', 'notification': payload},
        )
    except Exception:
        logger.exception('Notification %s was saved but could not be pushed', notification.pk)
    return notification.pk


@shared_task
def delete_expired_read_notifications(days=90):
    """Delete notifications that have been read longer than the retention window."""
    cutoff = timezone.now() - timedelta(days=days)
    deleted, _ = Notification.objects.filter(
        is_read=True,
        read_at__lt=cutoff,
    ).delete()
    return deleted
