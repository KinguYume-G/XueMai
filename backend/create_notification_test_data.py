"""
创建通知测试数据
用于测试通知功能
"""
import os
import sys
import django

# 设置 UTF-8 输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.notifications.models import Notification
from apps.users.models import User
from apps.posts.models import Post
from apps.comments.models import Comment
from django.utils import timezone
from datetime import timedelta


def create_test_notifications():
    """创建测试通知数据"""
    print("[START] Creating notification test data...\n")

    # 获取或创建测试用户
    try:
        # 尝试获取现有用户
        user = User.objects.filter(is_active=True).first()
        if not user:
            print("[ERROR] No active users found, please create a user first")
            return

        print(f"[OK] Found receiver: {user.username} (ID: {user.id})")

        # 获取其他用户作为发送者
        senders = list(User.objects.filter(is_active=True).exclude(id=user.id)[:5])
        if not senders:
            # 如果没有其他用户，创建几个测试用户
            print("[INFO] Creating test senders...")
            for i in range(1, 4):
                sender, created = User.objects.get_or_create(
                    username=f'testuser{i}',
                    defaults={
                        'email': f'test{i}@example.com',
                        'is_active': True
                    }
                )
                if created:
                    sender.set_password('testpass123')
                    sender.save()
                senders.append(sender)
                print(f"  [OK] Created sender: {sender.username}")
        else:
            print(f"[OK] Found {len(senders)} senders")

        # 获取测试帖子
        posts = list(Post.objects.all()[:3])
        if posts:
            print(f"[OK] Found {len(posts)} test posts")
        else:
            print("[WARN] No test posts found, some notifications may not have related posts")

        # 删除旧的测试通知
        old_count = Notification.objects.filter(user=user).count()
        if old_count > 0:
            print(f"[INFO] Deleting {old_count} old notifications...")
            Notification.objects.filter(user=user).delete()

        # 创建不同类型的通知
        notifications_data = []
        now = timezone.now()

        # 1. 点赞通知
        for i, sender in enumerate(senders[:3]):
            notifications_data.append({
                'user': user,
                'sender': sender,
                'type': 'like',
                'title': '收到新的赞',
                'content': f'{sender.username} 赞了你的帖子',
                'related_post': posts[0] if posts else None,
                'is_read': i > 1,  # 前2个未读
                'created_at': now - timedelta(minutes=i * 5),
            })

        # 2. 评论通知
        for i, sender in enumerate(senders[:3]):
            notifications_data.append({
                'user': user,
                'sender': sender,
                'type': 'comment',
                'title': '收到新评论',
                'content': f'{sender.username} 评论了你的帖子',
                'related_post': posts[1] if len(posts) > 1 else posts[0] if posts else None,
                'is_read': i > 1,  # 前2个未读
                'created_at': now - timedelta(hours=i + 1),
            })

        # 3. 关注通知
        for i, sender in enumerate(senders[:3]):
            notifications_data.append({
                'user': user,
                'sender': sender,
                'type': 'follow',
                'title': '新的关注',
                'content': f'{sender.username} 关注了你',
                'is_read': i > 1,  # 前2个未读
                'created_at': now - timedelta(hours=i * 2 + 3),
            })

        # 4. 系统通知
        system_notifications = [
            {
                'user': user,
                'sender': None,
                'type': 'system',
                'title': '欢迎使用 UniPulse Asia',
                'content': '感谢你加入我们的社区！快来发布你的第一篇帖子吧。',
                'is_read': True,
                'created_at': now - timedelta(days=1),
            },
            {
                'user': user,
                'sender': None,
                'type': 'system',
                'title': '系统维护通知',
                'content': '我们将在本周五晚上进行系统维护，届时服务可能会短暂中断。',
                'is_read': False,
                'created_at': now - timedelta(hours=6),
            },
            {
                'user': user,
                'sender': None,
                'type': 'system',
                'title': '新功能上线',
                'content': '我们上线了全新的通知系统，现在你可以更方便地查看和管理通知了！',
                'is_read': False,
                'created_at': now - timedelta(minutes=30),
            },
        ]
        notifications_data.extend(system_notifications)

        # 批量创建通知
        created_notifications = []
        for data in notifications_data:
            notification = Notification.objects.create(**data)
            created_notifications.append(notification)

        print(f"\n[SUCCESS] Created {len(created_notifications)} notifications!")

        # 统计信息
        unread_count = Notification.objects.filter(user=user, is_read=False).count()
        like_count = Notification.objects.filter(user=user, type='like', is_read=False).count()
        comment_count = Notification.objects.filter(user=user, type='comment', is_read=False).count()
        follow_count = Notification.objects.filter(user=user, type='follow', is_read=False).count()
        system_count = Notification.objects.filter(user=user, type='system', is_read=False).count()

        print(f"\n[STATS] Notification statistics:")
        print(f"  Total unread: {unread_count}")
        print(f"  Likes unread: {like_count}")
        print(f"  Comments unread: {comment_count}")
        print(f"  Follows unread: {follow_count}")
        print(f"  System unread: {system_count}")

        print(f"\n[DONE] Test data created successfully!")
        print(f"[INFO] You can now test these APIs:")
        print(f"  - GET http://127.0.0.1:8000/api/notifications/")
        print(f"  - GET http://127.0.0.1:8000/api/notifications/unread_count/")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    create_test_notifications()
