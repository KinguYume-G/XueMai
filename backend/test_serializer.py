import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer
from apps.users.models import User

# 获取接收者和通知
recipient = User.objects.get(id=14)
notif = Notification.objects.filter(user=recipient).select_related('sender', 'related_post').first()

print('=== 序列化器测试 ===')
print(f'\n原始通知数据:')
print(f'ID: {notif.id}')
print(f'类型: {notif.type}')
print(f'内容(content): {notif.content}')
print(f'发送者: {notif.sender.username if notif.sender else "系统"}')

# 序列化
serializer = NotificationSerializer(notif)
data = serializer.data

print(f'\n序列化后的数据:')
print(json.dumps(data, indent=2, ensure_ascii=False))

print(f'\n关键字段检查:')
print(f'✓ message字段存在: {"message" in data}')
print(f'✓ message内容: {data.get("message")}')
print(f'✓ notification_type字段: {data.get("notification_type")}')
print(f'✓ sender字段存在: {"sender" in data}')
if data.get("sender"):
    print(f'  - sender.username: {data["sender"].get("username")}')
print(f'✓ is_read字段: {data.get("is_read")}')
print(f'✓ time_ago字段: {data.get("time_ago")}')
