from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.notifications.models import Notification
from apps.posts.models import Post

User = get_user_model()


class Command(BaseCommand):
    help = "创建测试通知数据"

    def handle(self, *args, **options):
        # 清除旧数据
        Notification.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("[OK] 已清除旧通知数据"))

        # 获取接收者用户 (ID 14, Jeffrey)
        try:
            recipient = User.objects.get(id=14)
        except User.DoesNotExist:
            try:
                recipient = User.objects.get(email="g0184036940@gmail.com")
            except User.DoesNotExist:
                recipient = User.objects.first()

        self.stdout.write(
            f"[INFO] 接收者: {recipient.username} (ID: {recipient.id}, {recipient.email})"
        )

        # 获取发送者用户（至少8个）
        users = list(User.objects.exclude(id=recipient.id).order_by("id")[:8])
        posts = list(Post.objects.all()[:5])

        self.stdout.write("[INFO] 准备创建通知...")
        self.stdout.write(f"接收者: {recipient.username}")
        self.stdout.write(f"发送者数量: {len(users)}")
        self.stdout.write(f"帖子数量: {len(posts)}")

        # 创建通知
        notifications_created = 0

        # A. 点赞帖子通知（3条）
        if len(users) >= 3 and len(posts) >= 3:
            # 通知1 - 点赞帖子
            Notification.objects.create(
                user=recipient,
                sender=users[0],  # bob
                type="like",
                title="新的点赞",
                content=f"{users[0].username} 赞了你的帖子《{posts[0].title}》",
                related_post=posts[0],
                is_read=False,
            )
            notifications_created += 1

            # 通知2 - 点赞帖子
            Notification.objects.create(
                user=recipient,
                sender=users[1],  # charlie
                type="like",
                title="新的点赞",
                content=f"{users[1].username} 赞了你的帖子《{posts[1].title}》",
                related_post=posts[1],
                is_read=True,
            )
            notifications_created += 1

            # 通知3 - 点赞帖子
            Notification.objects.create(
                user=recipient,
                sender=users[5],  # grace
                type="like",
                title="新的点赞",
                content=f"{users[5].username} 赞了你的帖子《{posts[2].title}》",
                related_post=posts[2],
                is_read=False,
            )
            notifications_created += 1

        # B. 点赞评论通知（2条）
        if len(users) >= 4:
            # 通知4 - 点赞评论
            Notification.objects.create(
                user=recipient,
                sender=users[2],  # david
                type="like",
                title="新的点赞",
                content=f"{users[2].username} 赞了你的评论",
                is_read=False,
            )
            notifications_created += 1

            # 通知5 - 点赞评论
            Notification.objects.create(
                user=recipient,
                sender=users[3],  # emma
                type="like",
                title="新的点赞",
                content=f"{users[3].username} 赞了你的评论",
                is_read=True,
            )
            notifications_created += 1

        # C. 评论通知（2条）
        if len(users) >= 5 and len(posts) >= 2:
            # 通知6 - 评论帖子
            Notification.objects.create(
                user=recipient,
                sender=users[0],  # bob
                type="comment",
                title="新的评论",
                content=f"{users[0].username} 评论了你的帖子",
                related_post=posts[0],
                is_read=False,
            )
            notifications_created += 1

            # 通知7 - 评论帖子
            Notification.objects.create(
                user=recipient,
                sender=users[2],  # david
                type="comment",
                title="新的评论",
                content=f"{users[2].username} 评论了你的帖子：这个想法很不错！",
                related_post=posts[1],
                is_read=True,
            )
            notifications_created += 1

        # D. 关注通知（2条）
        if len(users) >= 6:
            # 通知8 - 关注
            Notification.objects.create(
                user=recipient,
                sender=users[1],  # charlie
                type="follow",
                title="新的关注",
                content=f"{users[1].username} 关注了你",
                is_read=False,
            )
            notifications_created += 1

            # 通知9 - 关注
            Notification.objects.create(
                user=recipient,
                sender=users[3],  # emma
                type="follow",
                title="新的关注",
                content=f"{users[3].username} 关注了你",
                is_read=True,
            )
            notifications_created += 1

        # E. 系统通知（2条）
        # 通知10 - 系统通知
        Notification.objects.create(
            user=recipient,
            sender=None,
            type="system",
            title="系统通知",
            content="新加坡国立大学交换项目申请截止日期：2025年12月08日",
            is_read=False,
        )
        notifications_created += 1

        # 通知11 - 系统通知
        if len(posts) >= 1:
            Notification.objects.create(
                user=recipient,
                sender=None,
                type="system",
                title="系统通知",
                content=f"你的帖子《{posts[0].title}》获得了热门推荐",
                related_post=posts[0],
                is_read=True,
            )
            notifications_created += 1

        self.stdout.write(self.style.SUCCESS(f"[OK] 成功创建 {notifications_created} 条通知"))

        # 显示统计
        total = Notification.objects.filter(user=recipient).count()
        unread = Notification.objects.filter(user=recipient, is_read=False).count()
        like_count = Notification.objects.filter(user=recipient, type="like").count()
        comment_count = Notification.objects.filter(user=recipient, type="comment").count()
        follow_count = Notification.objects.filter(user=recipient, type="follow").count()
        system_count = Notification.objects.filter(user=recipient, type="system").count()

        self.stdout.write("\n[STATS] 统计信息:")
        self.stdout.write(f"总通知数: {total}")
        self.stdout.write(f"未读通知: {unread}")
        self.stdout.write(f"点赞通知: {like_count}")
        self.stdout.write(f"评论通知: {comment_count}")
        self.stdout.write(f"关注通知: {follow_count}")
        self.stdout.write(f"系统通知: {system_count}")
