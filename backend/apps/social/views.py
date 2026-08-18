# Social views
from datetime import datetime, timezone as dt_timezone

from django.contrib.auth import get_user_model
from django.db.models import Count, F, Max, Prefetch, Q
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.notifications.utils import create_follow_notification
from core.pagination import StandardResultsPagination

from .models import (
    ChatGroup,
    ChatMessage,
    Follow,
    FriendRequest,
    GroupMember,
)
from .serializers import (
    ChatGroupSerializer,
    ChatMessageCreateSerializer,
    ChatMessageSerializer,
    FollowActionSerializer,
    FollowSerializer,
    FriendRequestCreateSerializer,
    FriendRequestSerializer,
    UserBasicSerializer,
)

User = get_user_model()


# ========== 关注系统视图 ==========


class FollowViewSet(viewsets.ReadOnlyModelViewSet):
    """关注关系API"""

    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination

    def get_queryset(self):
        """获取当前用户的关注/粉丝列表"""
        user_id = self.request.query_params.get("user_id", self.request.user.id)
        action_type = self.request.query_params.get("type", "following")

        if action_type == "followers":
            # 获取粉丝
            return Follow.objects.filter(following_id=user_id).select_related(
                "follower", "following", "follower__profile", "following__profile"
            )
        else:
            # 获取关注列表
            return Follow.objects.filter(follower_id=user_id).select_related(
                "follower", "following", "follower__profile", "following__profile"
            )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def follow_user(request):
    """关注用户"""
    serializer = FollowActionSerializer(data=request.data, context={"request": request})

    if not serializer.is_valid():
        return Response(
            {"data": None, "error": {"code": "validation_error", "message": serializer.errors}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    target_user_id = serializer.validated_data["user_id"]
    target_user = User.objects.get(id=target_user_id)

    follow, created = Follow.objects.get_or_create(follower=request.user, following=target_user)

    if created:
        # 更新计数
        if hasattr(request.user, "profile"):
            request.user.profile.following_count = F("following_count") + 1
            request.user.profile.save(update_fields=["following_count"])

        if hasattr(target_user, "profile"):
            target_user.profile.followers_count = F("followers_count") + 1
            target_user.profile.save(update_fields=["followers_count"])

        # 创建关注通知
        create_follow_notification(sender=request.user, following_user=target_user)

    return Response({"data": {"action": "followed", "user_id": target_user_id}, "error": None})


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def unfollow_user(request, user_id):
    """取消关注用户"""
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {"data": None, "error": {"code": "user_not_found", "message": "用户不存在"}},
            status=status.HTTP_404_NOT_FOUND,
        )

    deleted_count, _ = Follow.objects.filter(follower=request.user, following=target_user).delete()

    if deleted_count > 0:
        # 更新计数
        if hasattr(request.user, "profile"):
            request.user.profile.following_count = F("following_count") - 1
            request.user.profile.save(update_fields=["following_count"])

        if hasattr(target_user, "profile"):
            target_user.profile.followers_count = F("followers_count") - 1
            target_user.profile.save(update_fields=["followers_count"])

    return Response(status=status.HTTP_204_NO_CONTENT)


# ========== 聊天联系人列表视图 ==========


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_following_list(request):
    """
    获取关注列表（用于聊天）

    ✅ 优化：使用 Prefetch 预加载最后一条消息，避免 N+1 查询
    """
    user = request.user

    # 获取关注的用户 ID
    following = Follow.objects.filter(follower=user).values_list("following_id", flat=True)

    # ✅ 优化：预加载最后一条消息（发送和接收）
    last_sent_prefetch = Prefetch(
        "sent_messages",
        queryset=ChatMessage.objects.filter(to_user=user).order_by("-created_at")[:1],
        to_attr="cached_sent_messages",
    )

    last_received_prefetch = Prefetch(
        "received_messages",
        queryset=ChatMessage.objects.filter(from_user=user).order_by("-created_at")[:1],
        to_attr="cached_received_messages",
    )

    # 获取用户详细信息，包括未读消息数
    users = (
        User.objects.filter(id__in=following)
        .select_related("profile", "profile__school", "online_status")
        .prefetch_related(last_sent_prefetch, last_received_prefetch)
        .annotate(
            unread_count=Count(
                "sent_messages", filter=Q(sent_messages__to_user=user, sent_messages__is_read=False)
            )
        )
    )

    # 构建响应数据
    result = []
    for user_obj in users:
        # ✅ 使用预加载的消息，无需额外查询
        sent_msgs = user_obj.cached_sent_messages
        received_msgs = user_obj.cached_received_messages

        # 找出最后一条消息（发送或接收中较新的）
        last_msg = None
        if sent_msgs and received_msgs:
            last_msg = (
                sent_msgs[0]
                if sent_msgs[0].created_at > received_msgs[0].created_at
                else received_msgs[0]
            )
        elif sent_msgs:
            last_msg = sent_msgs[0]
        elif received_msgs:
            last_msg = received_msgs[0]

        last_message = None
        last_message_time = None
        if last_msg:
            last_message = {
                "content": last_msg.content,
                "created_at": last_msg.created_at.isoformat(),
                "is_read": last_msg.is_read,
                "from_me": last_msg.from_user_id == user.id,
            }
            last_message_time = last_msg.created_at

        result.append(
            {
                "user": UserBasicSerializer(user_obj).data,
                "unread_count": user_obj.unread_count,
                "last_message_time": last_message_time,
                "last_message": last_message,
                "is_online": (
                    user_obj.online_status.is_online
                    if hasattr(user_obj, "online_status")
                    else False
                ),
            }
        )

    # 按最后消息时间排序
    result.sort(
        key=lambda x: x["last_message_time"] or datetime.min.replace(tzinfo=dt_timezone.utc),
        reverse=True,
    )

    return Response({"count": len(result), "results": result})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_followers_list(request):
    """
    获取粉丝列表（用于聊天）

    ✅ 优化：使用 Prefetch 预加载最后一条消息，避免 N+1 查询
    """
    user = request.user

    # 获取粉丝用户 ID
    followers = Follow.objects.filter(following=user).values_list("follower_id", flat=True)

    # ✅ 优化：预加载最后一条消息（发送和接收）
    last_sent_prefetch = Prefetch(
        "sent_messages",
        queryset=ChatMessage.objects.filter(to_user=user).order_by("-created_at")[:1],
        to_attr="cached_sent_messages",
    )

    last_received_prefetch = Prefetch(
        "received_messages",
        queryset=ChatMessage.objects.filter(from_user=user).order_by("-created_at")[:1],
        to_attr="cached_received_messages",
    )

    # 获取用户详细信息
    users = (
        User.objects.filter(id__in=followers)
        .select_related("profile", "profile__school", "online_status")
        .prefetch_related(last_sent_prefetch, last_received_prefetch)
        .annotate(
            unread_count=Count(
                "sent_messages", filter=Q(sent_messages__to_user=user, sent_messages__is_read=False)
            )
        )
    )

    # 构建响应数据
    result = []
    for user_obj in users:
        # ✅ 使用预加载的消息，无需额外查询
        sent_msgs = user_obj.cached_sent_messages
        received_msgs = user_obj.cached_received_messages

        # 找出最后一条消息
        last_msg = None
        if sent_msgs and received_msgs:
            last_msg = (
                sent_msgs[0]
                if sent_msgs[0].created_at > received_msgs[0].created_at
                else received_msgs[0]
            )
        elif sent_msgs:
            last_msg = sent_msgs[0]
        elif received_msgs:
            last_msg = received_msgs[0]

        last_message = None
        last_message_time = None
        if last_msg:
            last_message = {
                "content": last_msg.content,
                "created_at": last_msg.created_at.isoformat(),
                "is_read": last_msg.is_read,
                "from_me": last_msg.from_user_id == user.id,
            }
            last_message_time = last_msg.created_at

        result.append(
            {
                "user": UserBasicSerializer(user_obj).data,
                "unread_count": user_obj.unread_count,
                "last_message_time": last_message_time,
                "last_message": last_message,
                "is_online": (
                    user_obj.online_status.is_online
                    if hasattr(user_obj, "online_status")
                    else False
                ),
            }
        )

    # 按最后消息时间排序
    result.sort(
        key=lambda x: x["last_message_time"] or datetime.min.replace(tzinfo=dt_timezone.utc),
        reverse=True,
    )

    return Response({"count": len(result), "results": result})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_friends_list(request):
    """
    获取好友列表（互相关注的用户）

    ✅ 优化：使用 Prefetch 预加载最后一条消息，避免 N+1 查询
    """
    user = request.user

    # 获取我关注的人
    following_ids = set(Follow.objects.filter(follower=user).values_list("following_id", flat=True))

    # 获取关注我的人
    follower_ids = set(Follow.objects.filter(following=user).values_list("follower_id", flat=True))

    # 取交集得到好友
    friend_ids = following_ids & follower_ids

    # ✅ 优化：预加载最后一条消息（发送和接收）
    last_sent_prefetch = Prefetch(
        "sent_messages",
        queryset=ChatMessage.objects.filter(to_user=user).order_by("-created_at")[:1],
        to_attr="cached_sent_messages",
    )

    last_received_prefetch = Prefetch(
        "received_messages",
        queryset=ChatMessage.objects.filter(from_user=user).order_by("-created_at")[:1],
        to_attr="cached_received_messages",
    )

    # 获取好友的详细信息
    users = (
        User.objects.filter(id__in=friend_ids)
        .select_related("profile", "profile__school", "online_status")
        .prefetch_related(last_sent_prefetch, last_received_prefetch)
        .annotate(
            unread_count=Count(
                "sent_messages", filter=Q(sent_messages__to_user=user, sent_messages__is_read=False)
            )
        )
    )

    # 构建响应数据
    result = []
    for user_obj in users:
        # ✅ 使用预加载的消息，无需额外查询
        sent_msgs = user_obj.cached_sent_messages
        received_msgs = user_obj.cached_received_messages

        # 找出最后一条消息
        last_msg = None
        if sent_msgs and received_msgs:
            last_msg = (
                sent_msgs[0]
                if sent_msgs[0].created_at > received_msgs[0].created_at
                else received_msgs[0]
            )
        elif sent_msgs:
            last_msg = sent_msgs[0]
        elif received_msgs:
            last_msg = received_msgs[0]

        last_message = None
        last_message_time = None
        if last_msg:
            last_message = {
                "content": last_msg.content,
                "created_at": last_msg.created_at.isoformat(),
                "is_read": last_msg.is_read,
                "from_me": last_msg.from_user_id == user.id,
            }
            last_message_time = last_msg.created_at

        result.append(
            {
                "user": UserBasicSerializer(user_obj).data,
                "unread_count": user_obj.unread_count,
                "last_message_time": last_message_time,
                "last_message": last_message,
                "is_online": (
                    user_obj.online_status.is_online
                    if hasattr(user_obj, "online_status")
                    else False
                ),
            }
        )

    # 按最后消息时间排序
    result.sort(
        key=lambda x: x["last_message_time"] or datetime.min.replace(tzinfo=dt_timezone.utc),
        reverse=True,
    )

    return Response({"count": len(result), "results": result})


# ========== 群组视图 ==========


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_groups_list(request):
    """获取当前用户加入的群组列表"""
    user = request.user

    # 获取用户加入的群组
    group_ids = GroupMember.objects.filter(user=user).values_list("group_id", flat=True)

    # 获取群组详细信息，包括未读消息数和最后消息时间
    groups = (
        ChatGroup.objects.filter(id__in=group_ids)
        .select_related("creator", "creator__profile")
        .annotate(
            unread_count=Count(
                "messages", filter=Q(messages__is_read=False) & ~Q(messages__from_user=user)
            ),
            last_message_time=Max("messages__created_at"),
        )
        .order_by("-last_message_time")
    )

    serializer = ChatGroupSerializer(groups, many=True)

    result = []
    for group_data in serializer.data:
        group_obj = next(g for g in groups if g.id == group_data["id"])
        result.append(
            {
                **group_data,
                "unread_count": group_obj.unread_count,
                "last_message_time": group_obj.last_message_time,
            }
        )

    return Response({"count": len(result), "results": result})


# ========== 好友申请视图 ==========


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_friend_requests(request):
    """获取收到的好友申请列表"""
    user = request.user

    requests_qs = (
        FriendRequest.objects.filter(to_user=user, status="pending")
        .select_related("from_user", "from_user__profile", "from_user__profile__school")
        .order_by("-created_at")
    )

    serializer = FriendRequestSerializer(requests_qs, many=True)

    return Response({"count": len(serializer.data), "results": serializer.data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_friend_request(request):
    """发送好友申请"""
    serializer = FriendRequestCreateSerializer(data=request.data, context={"request": request})

    if not serializer.is_valid():
        return Response(
            {"data": None, "error": {"code": "validation_error", "message": serializer.errors}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    to_user_id = serializer.validated_data["to_user_id"]
    to_user = User.objects.get(id=to_user_id)

    friend_request = FriendRequest.objects.create(from_user=request.user, to_user=to_user)

    result_serializer = FriendRequestSerializer(friend_request)

    return Response({"data": result_serializer.data, "error": None}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_friend_request(request, pk):
    """接受好友申请"""
    try:
        friend_request = FriendRequest.objects.select_related("from_user", "to_user").get(
            id=pk, to_user=request.user, status="pending"
        )
    except FriendRequest.DoesNotExist:
        return Response(
            {"data": None, "error": {"code": "not_found", "message": "好友申请不存在或已处理"}},
            status=status.HTTP_404_NOT_FOUND,
        )

    friend_request.accept()

    serializer = FriendRequestSerializer(friend_request)

    return Response({"data": serializer.data, "error": None})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reject_friend_request(request, pk):
    """拒绝好友申请"""
    try:
        friend_request = FriendRequest.objects.get(id=pk, to_user=request.user, status="pending")
    except FriendRequest.DoesNotExist:
        return Response(
            {"data": None, "error": {"code": "not_found", "message": "好友申请不存在或已处理"}},
            status=status.HTTP_404_NOT_FOUND,
        )

    friend_request.reject()

    serializer = FriendRequestSerializer(friend_request)

    return Response({"data": serializer.data, "error": None})


# ========== 聊天消息视图 ==========


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_messages(request):
    """获取聊天记录（私聊或群聊）"""
    user = request.user
    user_id = request.query_params.get("user_id")
    group_id = request.query_params.get("group_id")

    if bool(user_id) == bool(group_id):
        return Response(
            {
                "data": None,
                "error": {
                    "code": "invalid_params",
                    "message": "必须且只能指定 user_id 或 group_id",
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if user_id:
        # 获取私聊记录
        messages = (
            ChatMessage.objects.filter(
                Q(from_user=user, to_user_id=user_id) | Q(from_user_id=user_id, to_user=user)
            )
            .select_related("from_user", "from_user__profile", "to_user", "to_user__profile")
            .order_by("created_at")
        )
    else:
        # 获取群聊记录
        if not GroupMember.objects.filter(group_id=group_id, user=user).exists():
            return Response(
                {
                    "data": None,
                    "error": {"code": "forbidden", "message": "你不是该群组成员"},
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        messages = (
            ChatMessage.objects.filter(group_id=group_id)
            .select_related("from_user", "from_user__profile", "group")
            .order_by("created_at")
        )

    serializer = ChatMessageSerializer(messages, many=True)

    return Response({"count": len(serializer.data), "results": serializer.data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_message(request):
    """发送消息（私聊或群聊）"""
    serializer = ChatMessageCreateSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {"data": None, "error": {"code": "validation_error", "message": serializer.errors}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    data = serializer.validated_data
    to_user_id = data.get("to_user_id")
    group_id = data.get("group_id")

    if group_id and not GroupMember.objects.filter(
        group_id=group_id, user=request.user
    ).exists():
        return Response(
            {
                "data": None,
                "error": {"code": "forbidden", "message": "你不是该群组成员"},
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    message = ChatMessage.objects.create(
        from_user=request.user,
        to_user_id=to_user_id,
        group_id=group_id,
        content=data["content"],
        message_type=data.get("message_type", "text"),
    )

    result_serializer = ChatMessageSerializer(message)

    return Response({"data": result_serializer.data, "error": None}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_messages_as_read(request):
    """标记消息为已读"""
    user_id = request.data.get("user_id")
    group_id = request.data.get("group_id")

    if bool(user_id) == bool(group_id):
        return Response(
            {
                "data": None,
                "error": {
                    "code": "invalid_params",
                    "message": "必须且只能指定 user_id 或 group_id",
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if user_id:
        # 标记私聊消息为已读
        updated = ChatMessage.objects.filter(
            from_user_id=user_id, to_user=request.user, is_read=False
        ).update(is_read=True)
    else:
        if not GroupMember.objects.filter(group_id=group_id, user=request.user).exists():
            return Response(
                {
                    "data": None,
                    "error": {"code": "forbidden", "message": "你不是该群组成员"},
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        # ``is_read`` belongs to the message, not to each group member. Updating
        # it here would incorrectly mark the message as read for every member.
        updated = 0

    return Response({"data": {"marked_count": updated}, "error": None})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_unread_count(request):
    """获取未读消息总数"""
    user = request.user

    unread_count = ChatMessage.objects.filter(to_user=user, is_read=False).count()

    return Response({"total_unread": unread_count})


# ========== 搜索视图 ==========


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_users(request):
    """搜索用户"""
    query = request.query_params.get("q", "")
    search_type = request.query_params.get("type", "all")
    user = request.user

    if not query:
        return Response({"count": 0, "results": []})

    # 基础查询
    users_qs = (
        User.objects.filter(Q(username__icontains=query) | Q(email__icontains=query))
        .exclude(id=user.id)
        .select_related("profile", "profile__school")
    )

    # 根据搜索类型过滤
    if search_type == "following":
        following_ids = Follow.objects.filter(follower=user).values_list("following_id", flat=True)
        users_qs = users_qs.filter(id__in=following_ids)
    elif search_type == "followers":
        follower_ids = Follow.objects.filter(following=user).values_list("follower_id", flat=True)
        users_qs = users_qs.filter(id__in=follower_ids)
    elif search_type == "friends":
        following_ids = set(
            Follow.objects.filter(follower=user).values_list("following_id", flat=True)
        )
        follower_ids = set(
            Follow.objects.filter(following=user).values_list("follower_id", flat=True)
        )
        friend_ids = following_ids & follower_ids
        users_qs = users_qs.filter(id__in=friend_ids)

    users_qs = users_qs[:20]  # 限制返回20个结果

    serializer = UserBasicSerializer(users_qs, many=True)

    return Response({"count": len(serializer.data), "results": serializer.data})
