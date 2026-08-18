import os
import django
from datetime import timedelta
from django.utils import timezone

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.posts.models import Post
from apps.notifications.models import Notification

User = get_user_model()

# 清除旧数据
Notification.objects.all().delete()
print("✅ 已清除旧通知数据")

# 获取用户
try:
    recipient = User.objects.get(email='jeffrey@example.com')  # 改成你的邮箱
except User.DoesNotExist:
    recipient = User.objects.first()
    print(f"⚠️ 使用第一个用户作为接收者: {recipient.email}")

users = list(User.objects.exclude(id=recipient.id)[:5])
posts = list(Post.objects.all()[:3])

print(f"📝 准备创建通知...")
print(f"接收者: {recipient.username}")
print(f"发送者数量: {len(users)}")
print(f"帖子数量: {len(posts)}")

# 创建通知
notifications_created = 0

# 1. 点赞帖子通知
if len(users) > 0 and len(posts) > 0:
    Notification.objects.create(
        recipient=recipient,
        sender=users[0],
        notification_type='LIKE',
        title='新的点赞',
        message=f'{users[0].username} 赞了你的帖子《{posts[0].title}》',
        related_post=posts[0],
        is_read=False,
        created_at=timezone.now() - timedelta(minutes=5)
    )
    notifications_created += 1

if len(users) > 1 and len(posts) > 1:
    Notification.objects.create(
        recipient=recipient,
        sender=users[1],
        notification_type='LIKE',
        title='新的点赞',
        message=f'{users[1].username} 赞了你的帖子《{posts[1].title}》',
        related_post=posts[1],
        is_read=True,
        created_at=timezone.now() - timedelta(hours=3)
    )
    notifications_created += 1

# 2. 点赞评论通知
if len(users) > 2:
    Notification.objects.create(
        recipient=recipient,
        sender=users[2],
        notification_type='LIKE',
        title='新的点赞',
        message=f'{users[2].username} 赞了你的评论',
        is_read=False,
        created_at=timezone.now() - timedelta(hours=1)
    )
    notifications_created += 1

# 3. 评论通知
if len(users) > 3 and len(posts) > 2:
    Notification.objects.create(
        recipient=recipient,
        sender=users[3],
        notification_type='COMMENT',
        title='新的评论',
        message=f'{users[3].username} 评论了你的帖子',
        related_post=posts[2],
        is_read=False,
        created_at=timezone.now() - timedelta(hours=2)
    )
    notifications_created += 1

# 4. 关注通知
if len(users) > 4:
    Notification.objects.create(
        recipient=recipient,
        sender=users[4],
        notification_type='FOLLOW',
        title='新的关注',
        message=f'{users[4].username} 关注了你',
        is_read=False,
        created_at=timezone.now() - timedelta(days=1)
    )
    notifications_created += 1

# 5. 系统通知
Notification.objects.create(
    recipient=recipient,
    sender=None,
    notification_type='SYSTEM',
    title='系统通知',
    message='新加坡国立大学交换项目申请截止日期：2025-12-08',
    is_read=False,
    created_at=timezone.now() - timedelta(days=2)
)
notifications_created += 1

print(f"✅ 成功创建 {notifications_created} 条通知")

# 显示统计
total = Notification.objects.filter(recipient=recipient).count()
unread = Notification.objects.filter(recipient=recipient, is_read=False).count()
like_count = Notification.objects.filter(recipient=recipient, notification_type='LIKE').count()
comment_count = Notification.objects.filter(recipient=recipient, notification_type='COMMENT').count()
follow_count = Notification.objects.filter(recipient=recipient, notification_type='FOLLOW').count()
system_count = Notification.objects.filter(recipient=recipient, notification_type='SYSTEM').count()

print(f"\n📊 统计信息:")
print(f"总通知数: {total}")
print(f"未读通知: {unread}")
print(f"点赞通知: {like_count}")
print(f"评论通知: {comment_count}")
print(f"关注通知: {follow_count}")
print(f"系统通知: {system_count}")
