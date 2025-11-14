# Comments views
from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F

from .models import Comment
from .serializers import CommentSerializer, CommentCreateSerializer, CommentWithRepliesSerializer
from core.pagination import StandardResultsPagination
from apps.notifications.utils import create_comment_notification


class CommentViewSet(viewsets.ModelViewSet):
    """评论API"""
    queryset = Comment.objects.select_related('author', 'post', 'parent').all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['post', 'parent', 'author']
    ordering_fields = ['created_at', 'likes_count']
    ordering = ['created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        elif self.action == 'list' and self.request.query_params.get('with_replies'):
            return CommentWithRepliesSerializer
        return CommentSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 如果查询参数中指定了帖子ID，只返回该帖子的顶级评论
        post_id = self.request.query_params.get('post')
        if post_id and self.action == 'list':
            queryset = queryset.filter(post_id=post_id, parent__isnull=True)
        
        return queryset
    
    def perform_create(self, serializer):
        comment = serializer.save(author=self.request.user)

        # 更新帖子评论数
        post = comment.post
        post.comments_count = F('comments_count') + 1
        post.save(update_fields=['comments_count'])

        # 创建评论通知
        create_comment_notification(
            sender=self.request.user,
            post=comment.post if not comment.parent else None,
            parent_comment=comment.parent,
            comment=comment
        )
    
    def perform_destroy(self, instance):
        # 更新帖子评论数
        post = instance.post
        post.comments_count = F('comments_count') - 1
        post.save(update_fields=['comments_count'])
        instance.delete()
