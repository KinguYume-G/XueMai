"""
通知创建工具函数
"""

from .models import Notification


def create_like_notification(sender, post=None, comment=None):
    """
    创建点赞通知

    Args:
        sender: 点赞的用户
        post: 被点赞的帖子（可选）
        comment: 被点赞的评论（可选）
    """
    if post:
        # 点赞帖子 - 通知帖子作者
        recipient = post.author
        title = "新的点赞"
        content = f"{sender.username} 赞了你的帖子《{post.title}》"
    elif comment:
        # 点赞评论 - 通知评论作者
        recipient = comment.author
        title = "新的点赞"
        content = f"{sender.username} 赞了你的评论"
    else:
        return None

    # 不给自己创建通知
    if recipient == sender:
        return None

    notification = Notification.objects.create(
        user=recipient,
        sender=sender,
        type="like",
        title=title,
        content=content,
        related_post=post,
        related_comment=comment,
    )

    return notification


def create_comment_notification(sender, post=None, parent_comment=None, comment=None):
    """
    创建评论通知

    Args:
        sender: 评论的用户
        post: 被评论的帖子（可选）
        parent_comment: 被回复的评论（可选）
        comment: 新创建的评论对象（可选）
    """
    if post and not parent_comment:
        # 评论帖子 - 通知帖子作者
        recipient = post.author
        title = "新的评论"
        content = f"{sender.username} 评论了你的帖子"
    elif parent_comment:
        # 回复评论 - 通知被回复评论的作者
        recipient = parent_comment.author
        title = "新的评论"
        content = f"{sender.username} 回复了你的评论"
        post = parent_comment.post  # 关联到原帖子
    else:
        return None

    # 不给自己创建通知
    if recipient == sender:
        return None

    notification = Notification.objects.create(
        user=recipient,
        sender=sender,
        type="comment",
        title=title,
        content=content,
        related_post=post,
        related_comment=comment or parent_comment,
    )

    return notification


def create_follow_notification(sender, following_user):
    """
    创建关注通知

    Args:
        sender: 关注的用户（关注者）
        following_user: 被关注的用户
    """
    # 不给自己创建通知
    if following_user == sender:
        return None

    notification = Notification.objects.create(
        user=following_user,
        sender=sender,
        type="follow",
        title="新的关注",
        content=f"{sender.username} 关注了你",
    )

    return notification


def create_system_notification(user, title, content, link=None):
    """
    创建系统通知

    Args:
        user: 接收通知的用户
        title: 通知标题
        content: 通知内容
        link: 链接（可选）
    """
    notification = Notification.objects.create(
        user=user,
        sender=None,  # 系统通知无发送者
        type="system",
        title=title,
        content=content,
        link=link or "",
    )

    return notification
