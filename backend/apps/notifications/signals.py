"""
通知信号处理器
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.comments.models import Comment
from apps.posts.models import PostLike
from apps.social.models import Follow, Like

from .models import Notification


@receiver(post_save, sender=PostLike)
def notify_post_like(sender, instance, created, **kwargs):
    """帖子被点赞时通知作者"""
    if created and instance.user != instance.post.author:
        Notification.objects.create(
            user=instance.post.author,
            type="like",
            title=f"{instance.user.username} 点赞了你的帖子",
            content=instance.post.title[:50] if instance.post.title else instance.post.body[:50],
            link=f"/posts/{instance.post.id}",
        )


@receiver(post_save, sender=Comment)
def notify_post_comment(sender, instance, created, **kwargs):
    """帖子被评论时通知作者"""
    if created:
        if instance.parent:
            # 回复评论 - 通知原评论作者
            if instance.author != instance.parent.author:
                Notification.objects.create(
                    user=instance.parent.author,
                    type="comment",
                    title=f"{instance.author.username} 回复了你的评论",
                    content=instance.content[:50],
                    link=f"/posts/{instance.post.id}#comment-{instance.id}",
                )
        else:
            # 新评论 - 通知帖子作者
            if instance.author != instance.post.author:
                Notification.objects.create(
                    user=instance.post.author,
                    type="comment",
                    title=f"{instance.author.username} 评论了你的帖子",
                    content=instance.content[:50],
                    link=f"/posts/{instance.post.id}#comment-{instance.id}",
                )


@receiver(post_save, sender=Follow)
def notify_new_follower(sender, instance, created, **kwargs):
    """被关注时通知用户"""
    if created:
        Notification.objects.create(
            user=instance.following,
            type="follow",
            title=f"{instance.follower.username} 关注了你",
            content="",
            link=f"/users/{instance.follower.id}",
        )


@receiver(post_save, sender=Like)
def notify_like(sender, instance, created, **kwargs):
    """点赞时通知"""
    if created:
        if instance.post and instance.user != instance.post.author:
            Notification.objects.create(
                user=instance.post.author,
                type="like",
                title=f"{instance.user.username} 点赞了你的帖子",
                content="",
                link=f"/posts/{instance.post.id}",
            )
        elif instance.comment and instance.user != instance.comment.author:
            Notification.objects.create(
                user=instance.comment.author,
                type="like",
                title=f"{instance.user.username} 点赞了你的评论",
                content=instance.comment.content[:50],
                link=f"/posts/{instance.comment.post.id}#comment-{instance.comment.id}",
            )
