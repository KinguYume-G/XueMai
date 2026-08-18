# Notifications serializers
from datetime import datetime

from django.utils import timezone
from rest_framework import serializers

from apps.comments.models import Comment
from apps.posts.models import Post
from apps.users.models import User

from .models import Notification


class SenderSerializer(serializers.ModelSerializer):
    """发送者信息"""

    avatar = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "full_name", "avatar"]

    def get_avatar(self, obj):
        if hasattr(obj, "profile") and obj.profile and obj.profile.avatar_url:
            return obj.profile.avatar_url
        return None

    def get_full_name(self, obj):
        if hasattr(obj, "profile") and obj.profile:
            # 优先使用 profile 中的名字字段
            if hasattr(obj.profile, "full_name") and obj.profile.full_name:
                return obj.profile.full_name
        # 回退到 username
        return obj.username


class RelatedPostSerializer(serializers.ModelSerializer):
    """关联帖子信息"""

    class Meta:
        model = Post
        fields = ["id", "title"]


class RelatedCommentSerializer(serializers.ModelSerializer):
    """关联评论信息"""

    class Meta:
        model = Comment
        fields = ["id", "content"]


class NotificationSerializer(serializers.ModelSerializer):
    sender = SenderSerializer(read_only=True)
    related_post = RelatedPostSerializer(read_only=True)
    related_comment = RelatedCommentSerializer(read_only=True)
    time_ago = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()
    notification_type = serializers.CharField(source="type", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "notification_type",
            "type",  # 保留原字段兼容性
            "title",
            "content",
            "message",
            "sender",
            "related_post",
            "related_comment",
            "link",
            "is_read",
            "created_at",
            "read_at",
            "time_ago",
        ]
        read_only_fields = [
            "id",
            "notification_type",
            "type",
            "title",
            "content",
            "message",
            "sender",
            "related_post",
            "related_comment",
            "link",
            "created_at",
            "read_at",
            "time_ago",
        ]

    def get_message(self, obj):
        """生成格式化的消息文本"""
        # 如果已经有 content，直接返回
        if obj.content:
            return obj.content

        # 否则根据类型生成消息
        sender_name = obj.sender.username if obj.sender else "系统"

        if obj.type == "like":
            if obj.related_post:
                return f"{sender_name} 赞了你的帖子《{obj.related_post.title}》"
            elif obj.related_comment:
                return f"{sender_name} 赞了你的评论"
            return f"{sender_name} 赞了你的内容"

        elif obj.type == "comment":
            if obj.related_post:
                return f"{sender_name} 评论了你的帖子"
            return f"{sender_name} 回复了你的评论"

        elif obj.type == "follow":
            return f"{sender_name} 关注了你"

        elif obj.type == "system":
            return obj.title

        return obj.content or obj.title

    def get_time_ago(self, obj):
        """计算相对时间"""
        if not obj.created_at:
            return ""

        now = timezone.now()
        diff = now - obj.created_at

        seconds = diff.total_seconds()
        minutes = seconds / 60
        hours = minutes / 60
        days = hours / 24

        if seconds < 60:
            return "刚刚"
        elif minutes < 60:
            return f"{int(minutes)}分钟前"
        elif hours < 24:
            return f"{int(hours)}小时前"
        elif days < 2:
            return "昨天"
        elif days < 7:
            return f"{int(days)}天前"
        else:
            # 返回具体日期 "MM月DD日"
            return obj.created_at.strftime("%m月%d日")
