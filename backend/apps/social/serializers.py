# Social serializers
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import (
    ChatGroup,
    ChatMessage,
    Follow,
    FriendRequest,
    GroupMember,
    UserOnlineStatus,
)

User = get_user_model()


# ========== 基础序列化器 ==========


class UserBasicSerializer(serializers.ModelSerializer):
    """基础用户信息序列化器（用于嵌套）"""

    avatar = serializers.SerializerMethodField()
    school = serializers.SerializerMethodField()
    major = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "avatar", "school", "major"]
        read_only_fields = ["id", "username", "email"]

    def get_avatar(self, obj):
        if hasattr(obj, "profile") and obj.profile.avatar_url:
            return obj.profile.avatar_url
        return None

    def get_school(self, obj):
        if hasattr(obj, "profile") and obj.profile.school:
            return obj.profile.school.name
        return None

    def get_major(self, obj):
        if hasattr(obj, "profile"):
            return obj.profile.major
        return None


# ========== 关注系统序列化器 ==========


class FollowSerializer(serializers.ModelSerializer):
    follower = UserBasicSerializer(read_only=True)
    following = UserBasicSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ["id", "follower", "following", "created_at"]
        read_only_fields = ["created_at"]


class FollowActionSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def validate_user_id(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("用户不存在")

        # 不能关注自己
        request = self.context.get("request")
        if request and request.user.id == value:
            raise serializers.ValidationError("不能关注自己")

        return value


# ========== 好友申请序列化器 ==========


class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = UserBasicSerializer(read_only=True)
    to_user = UserBasicSerializer(read_only=True)

    class Meta:
        model = FriendRequest
        fields = ["id", "from_user", "to_user", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "status", "created_at", "updated_at"]


class FriendRequestCreateSerializer(serializers.Serializer):
    to_user_id = serializers.IntegerField()

    def validate_to_user_id(self, value):
        request = self.context.get("request")

        # 检查用户是否存在
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("用户不存在")

        # 不能给自己发送申请
        if request and request.user.id == value:
            raise serializers.ValidationError("不能向自己发送好友申请")

        # 检查是否已经是好友
        if request:
            is_friend = (
                Follow.objects.filter(follower=request.user, following_id=value).exists()
                and Follow.objects.filter(follower_id=value, following=request.user).exists()
            )
            if is_friend:
                raise serializers.ValidationError("你们已经是好友了")

        # 检查是否已有待处理的申请
        if (
            request
            and FriendRequest.objects.filter(
                from_user=request.user, to_user_id=value, status="pending"
            ).exists()
        ):
            raise serializers.ValidationError("你已经发送过好友申请了")

        if (
            request
            and FriendRequest.objects.filter(
                from_user_id=value, to_user=request.user, status="pending"
            ).exists()
        ):
            raise serializers.ValidationError("对方已经向你发送了好友申请，请直接处理该申请")

        return value


# ========== 群组序列化器 ==========


class ChatGroupBasicSerializer(serializers.ModelSerializer):
    """简化的群组序列化器（用于嵌套）"""

    class Meta:
        model = ChatGroup
        fields = ["id", "name", "avatar_url"]
        read_only_fields = ["id"]


class ChatGroupSerializer(serializers.ModelSerializer):
    creator = UserBasicSerializer(read_only=True)

    class Meta:
        model = ChatGroup
        fields = [
            "id",
            "name",
            "description",
            "avatar_url",
            "creator",
            "member_count",
            "created_at",
        ]
        read_only_fields = ["id", "member_count", "created_at"]


class GroupMemberSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    group = ChatGroupBasicSerializer(read_only=True)

    class Meta:
        model = GroupMember
        fields = ["id", "group", "user", "role", "joined_at"]
        read_only_fields = ["id", "joined_at"]


# ========== 聊天消息序列化器 ==========


class ChatMessageSerializer(serializers.ModelSerializer):
    from_user = UserBasicSerializer(read_only=True)
    to_user = UserBasicSerializer(read_only=True)
    group = ChatGroupBasicSerializer(read_only=True)

    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "from_user",
            "to_user",
            "group",
            "content",
            "message_type",
            "is_read",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ChatMessageCreateSerializer(serializers.Serializer):
    to_user_id = serializers.IntegerField(required=False, allow_null=True)
    group_id = serializers.IntegerField(required=False, allow_null=True)
    content = serializers.CharField()
    message_type = serializers.ChoiceField(
        choices=["text", "image", "file", "emoji"], default="text"
    )

    def validate(self, attrs):
        to_user_id = attrs.get("to_user_id")
        group_id = attrs.get("group_id")

        # 必须指定接收者（私聊或群聊）
        if not to_user_id and not group_id:
            raise serializers.ValidationError("必须指定接收者（to_user_id 或 group_id）")

        # 不能同时指定两个
        if to_user_id and group_id:
            raise serializers.ValidationError("不能同时指定 to_user_id 和 group_id")

        # 验证接收用户是否存在
        if to_user_id and not User.objects.filter(id=to_user_id).exists():
            raise serializers.ValidationError("接收用户不存在")

        # 验证群组是否存在
        if group_id and not ChatGroup.objects.filter(id=group_id).exists():
            raise serializers.ValidationError("群组不存在")

        return attrs


# ========== 用户在线状态序列化器 ==========


class UserOnlineStatusSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = UserOnlineStatus
        fields = ["user_id", "is_online", "last_seen", "status_text"]
        read_only_fields = ["last_seen"]
