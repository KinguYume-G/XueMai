# Comments serializers
from rest_framework import serializers

from apps.users.serializers import UserPublicSerializer

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)
    is_reply = serializers.BooleanField(source="parent", read_only=True)
    # ✅ 优化：使用 annotate 的值，避免 N+1 查询
    replies_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "author",
            "content",
            "parent",
            "is_reply",
            "likes_count",
            "replies_count",
            "created_at",
        ]
        read_only_fields = ["author", "likes_count", "created_at"]

    def validate_content(self, value):
        if len(value) > 1000:
            raise serializers.ValidationError("评论不能超过1000字符")
        return value


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["post", "content", "parent"]

    def validate_parent(self, value):
        """验证父评论必须属于同一帖子"""
        if value:
            post = self.initial_data.get("post")
            if value.post_id != int(post):
                raise serializers.ValidationError("父评论必须属于同一帖子")
        return value


class CommentWithRepliesSerializer(CommentSerializer):
    """带回复的评论序列化器"""

    replies = serializers.SerializerMethodField()

    class Meta(CommentSerializer.Meta):
        fields = [*CommentSerializer.Meta.fields, "replies"]

    def get_replies(self, obj):
        """
        获取评论的回复

        ✅ 优化：使用 Prefetch 预加载的数据，避免 N+1 查询
        ViewSet 已通过 prefetch_related 预加载回复
        """
        if obj.parent is None:  # 只为顶级评论获取回复
            # 使用已预加载的回复（如果存在）
            replies = obj.replies.all()
            return CommentSerializer(replies, many=True).data
        return []
