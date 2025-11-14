import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.notifications.models import Notification
from apps.users.models import User

# 获取接收者
recipient = User.objects.get(id=14)

# 获取最新5条通知
notifs = Notification.objects.filter(user=recipient).select_related('sender', 'related_post').order_by('-created_at')[:5]

print('=== 最新5条通知详情 ===')
print(f'接收者: {recipient.username} (ID: {recipient.id}, {recipient.email})\n')

for i, n in enumerate(notifs, 1):
    print(f'[{i}] 通知ID: {n.id}')
    print(f'    类型: {n.type}')
    print(f'    标题: {n.title}')
    print(f'    内容: {n.content}')
    print(f'    发送者: {n.sender.username if n.sender else "系统"}')
    print(f'    未读: {"是" if not n.is_read else "否"}')
    if n.related_post:
        print(f'    关联帖子: {n.related_post.title}')
    print()

# 统计信息
total = Notification.objects.filter(user=recipient).count()
unread = Notification.objects.filter(user=recipient, is_read=False).count()
like_count = Notification.objects.filter(user=recipient, type='like').count()
comment_count = Notification.objects.filter(user=recipient, type='comment').count()
follow_count = Notification.objects.filter(user=recipient, type='follow').count()
system_count = Notification.objects.filter(user=recipient, type='system').count()

print('=== 统计信息 ===')
print(f'总通知数: {total}')
print(f'未读通知: {unread}')
print(f'点赞通知: {like_count}')
print(f'评论通知: {comment_count}')
print(f'关注通知: {follow_count}')
print(f'系统通知: {system_count}')
