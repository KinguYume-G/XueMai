# Comments views
from django.db.models import F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.notifications.utils import create_comment_notification
from core.pagination import StandardResultsPagination
from core.permissions import IsOwnerOrStaff

from .models import Comment
from .serializers import (
    CommentCreateSerializer,
    CommentSerializer,
    CommentWithRepliesSerializer,
)


class CommentViewSet(viewsets.ModelViewSet):
    """评论API"""

    queryset = Comment.objects.select_related("author", "post", "parent").all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrStaff]
    owner_fields = ("author",)
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["post", "parent", "author"]
    ordering_fields = ["created_at", "likes_count"]
    ordering = ["created_at"]

    def get_serializer_class(self):
        if self.action == "create":
            return CommentCreateSerializer
        elif self.action == "list" and self.request.query_params.get("with_replies"):
            return CommentWithRepliesSerializer
        return CommentSerializer

    def get_queryset(self):
        """
        优化的查询集，避免 N+1 查询问题

        优化内容：
        1. select_related 预加载作者和关联对象
        2. annotate 预计算回复数
        3. prefetch_related 条件预加载回复
        """
        from django.db.models import Count, Prefetch

        queryset = super().get_queryset()

        # 1. 预加载作者和关联对象（避免 N+1）
        queryset = queryset.select_related(
            "author", "author__profile", "post", "parent"  # ✅ 新增：预加载作者资料
        )

        # 2. 预计算回复数（避免每个评论都查询一次）
        queryset = queryset.annotate(replies_count=Count("replies"))

        # 3. 如果请求带回复，预加载它们（避免 N+1）
        if self.request.query_params.get("with_replies"):
            replies_queryset = Comment.objects.select_related("author", "author__profile").order_by(
                "created_at"
            )

            queryset = queryset.prefetch_related(Prefetch("replies", queryset=replies_queryset))

        # 4. 如果查询参数中指定了帖子ID，只返回该帖子的顶级评论
        post_id = self.request.query_params.get("post")
        if post_id and self.action == "list":
            queryset = queryset.filter(post_id=post_id, parent__isnull=True)

        return queryset

    def perform_create(self, serializer):
        comment = serializer.save(author=self.request.user)

        # 更新帖子评论数
        post = comment.post
        post.comments_count = F("comments_count") + 1
        post.save(update_fields=["comments_count"])

        # 创建评论通知
        create_comment_notification(
            sender=self.request.user,
            post=comment.post if not comment.parent else None,
            parent_comment=comment.parent,
            comment=comment,
        )

    def perform_destroy(self, instance):
        # 更新帖子评论数
        post = instance.post
        post.comments_count = max(0, post.comments_count - 1)
        post.save(update_fields=["comments_count"])
        instance.delete()
