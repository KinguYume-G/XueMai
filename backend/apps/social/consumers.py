from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone

from .models import ChatMessage, GroupMember, UserOnlineStatus
from .serializers import ChatMessageCreateSerializer, ChatMessageSerializer


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """Deliver private/group messages and user presence events."""

    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close(code=4401)
            return

        self.user_group = f'user_{self.user.pk}'
        await self.channel_layer.group_add(self.user_group, self.channel_name)

        self.chat_groups = await self._group_names()
        for group_name in self.chat_groups:
            await self.channel_layer.group_add(group_name, self.channel_name)

        await self._set_presence(True)
        await self.accept()
        await self.channel_layer.group_send(
            'presence',
            {'type': 'presence.changed', 'user_id': self.user.pk, 'is_online': True},
        )
        await self.channel_layer.group_add('presence', self.channel_name)

    async def disconnect(self, close_code):
        if not getattr(self, 'user', None) or not self.user.is_authenticated:
            return
        await self._set_presence(False)
        await self.channel_layer.group_discard(self.user_group, self.channel_name)
        for group_name in getattr(self, 'chat_groups', []):
            await self.channel_layer.group_discard(group_name, self.channel_name)
        await self.channel_layer.group_discard('presence', self.channel_name)
        await self.channel_layer.group_send(
            'presence',
            {
                'type': 'presence.changed',
                'user_id': self.user.pk,
                'is_online': False,
                'last_seen': timezone.now().isoformat(),
            },
        )

    async def receive_json(self, content, **kwargs):
        if content.get('type') != 'message.send':
            await self.send_json({'type': 'error', 'message': 'Unsupported event type'})
            return

        serializer = ChatMessageCreateSerializer(
            data=content.get('payload', {}),
            context={'user': self.user},
        )
        if not serializer.is_valid():
            await self.send_json({'type': 'error', 'errors': serializer.errors})
            return

        message = await self._create_message(serializer.validated_data)
        if not message:
            await self.send_json({'type': 'error', 'message': 'You are not a member of this group'})
            return

        payload = await self._serialize_message(message)
        target = f'chat_group_{message.group_id}' if message.group_id else f'user_{message.to_user_id}'
        await self.channel_layer.group_send(target, {'type': 'chat.message', 'message': payload})
        if target != self.user_group:
            await self.channel_layer.group_send(
                self.user_group,
                {'type': 'chat.message', 'message': payload},
            )

    async def chat_message(self, event):
        await self.send_json({'type': 'message.created', 'payload': event['message']})

    async def presence_changed(self, event):
        await self.send_json({
            'type': 'presence.changed',
            'payload': {
                'user_id': event['user_id'],
                'is_online': event['is_online'],
                'last_seen': event.get('last_seen'),
            },
        })

    async def notification_created(self, event):
        await self.send_json({
            'type': 'notification.created',
            'payload': event['notification'],
        })

    @database_sync_to_async
    def _group_names(self):
        return [
            f'chat_group_{group_id}'
            for group_id in GroupMember.objects.filter(user=self.user)
            .values_list('group_id', flat=True)
        ]

    @database_sync_to_async
    def _set_presence(self, is_online):
        status, _ = UserOnlineStatus.objects.get_or_create(user=self.user)
        status.is_online = is_online
        status.save(update_fields=['is_online', 'last_seen'])

    @database_sync_to_async
    def _create_message(self, data):
        group_id = data.get('group_id')
        if group_id and not GroupMember.objects.filter(group_id=group_id, user=self.user).exists():
            return None
        return ChatMessage.objects.create(
            from_user=self.user,
            to_user_id=data.get('to_user_id'),
            group_id=group_id,
            content=data['content'],
            message_type=data.get('message_type', 'text'),
        )

    @database_sync_to_async
    def _serialize_message(self, message):
        message = ChatMessage.objects.select_related(
            'from_user', 'from_user__profile', 'to_user', 'to_user__profile', 'group'
        ).get(pk=message.pk)
        return ChatMessageSerializer(message).data
