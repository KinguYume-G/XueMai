"""
通知信号处理器
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from apps.posts.models import PostLike
from apps.comments.models import Comment
from apps.social.models import Follow, Like
from .tasks import create_notification_task


def queue_notification(**payload):
    def dispatch():
        try:
            create_notification_task.delay(**payload)
        except Exception:
            create_notification_task.apply(kwargs=payload)

    transaction.on_commit(dispatch)


@receiver(post_save, sender=PostLike)
def notify_post_like(sender, instance, created, **kwargs):
    """帖子被点赞时通知作者"""
    if created and instance.user != instance.post.author:
        queue_notification(
            user_id=instance.post.author_id,
            sender_id=instance.user_id,
            notification_type='like',
            title=f'{instance.user.username} 点赞了你的帖子',
            content=instance.post.title[:50] if instance.post.title else instance.post.body[:50],
            link=f'/posts/{instance.post.id}',
            related_post_id=instance.post_id,
        )


@receiver(post_save, sender=Comment)
def notify_post_comment(sender, instance, created, **kwargs):
    """帖子被评论时通知作者"""
    if created:
        if instance.parent:
            # 回复评论 - 通知原评论作者
            if instance.author != instance.parent.author:
                queue_notification(
                    user_id=instance.parent.author_id,
                    sender_id=instance.author_id,
                    notification_type='comment',
                    title=f'{instance.author.username} 回复了你的评论',
                    content=instance.content[:50],
                    link=f'/posts/{instance.post.id}#comment-{instance.id}',
                    related_post_id=instance.post_id,
                    related_comment_id=instance.id,
                )
        else:
            # 新评论 - 通知帖子作者
            if instance.author != instance.post.author:
                queue_notification(
                    user_id=instance.post.author_id,
                    sender_id=instance.author_id,
                    notification_type='comment',
                    title=f'{instance.author.username} 评论了你的帖子',
                    content=instance.content[:50],
                    link=f'/posts/{instance.post.id}#comment-{instance.id}',
                    related_post_id=instance.post_id,
                    related_comment_id=instance.id,
                )


@receiver(post_save, sender=Follow)
def notify_new_follower(sender, instance, created, **kwargs):
    """被关注时通知用户"""
    if created:
        queue_notification(
            user_id=instance.following_id,
            sender_id=instance.follower_id,
            notification_type='follow',
            title=f'{instance.follower.username} 关注了你',
            content='',
            link=f'/users/{instance.follower.id}',
        )


@receiver(post_save, sender=Like)
def notify_like(sender, instance, created, **kwargs):
    """点赞时通知"""
    if created:
        if instance.post and instance.user != instance.post.author:
            queue_notification(
                user_id=instance.post.author_id,
                sender_id=instance.user_id,
                notification_type='like',
                title=f'{instance.user.username} 点赞了你的帖子',
                content='',
                link=f'/posts/{instance.post.id}',
                related_post_id=instance.post_id,
            )
        elif instance.comment and instance.user != instance.comment.author:
            queue_notification(
                user_id=instance.comment.author_id,
                sender_id=instance.user_id,
                notification_type='like',
                title=f'{instance.user.username} 点赞了你的评论',
                content=instance.comment.content[:50],
                link=f'/posts/{instance.comment.post.id}#comment-{instance.comment.id}',
                related_post_id=instance.comment.post_id,
                related_comment_id=instance.comment_id,
            )
