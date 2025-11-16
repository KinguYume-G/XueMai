# Posts views
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import F, ExpressionWrapper, FloatField, functions
from datetime import timedelta

from .models import Tag, Post, PostLike, Bookmark
from .serializers import TagSerializer, PostSerializer, PostCreateUpdateSerializer
from core.pagination import StandardResultsPagination
from apps.notifications.utils import create_like_notification


class PostViewSet(viewsets.ModelViewSet):
    """帖子API"""
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['visibility', 'is_published', 'author']
    search_fields = ['title', 'body']
    ordering_fields = ['created_at', 'likes_count', 'comments_count']
    
    def get_permissions(self):
        """允许匿名用户查看列表和详情"""
        if self.action in ['list', 'retrieve', 'feed']:
            return [AllowAny()]
        return super().get_permissions()
    
   
    def get_queryset(self):
        user = self.request.user
        queryset = Post.objects.visible_to(user).select_related(
            'author', 
            'author__profile', 
            'target_university'
        ).prefetch_related(
            'tags'
        )
        
        # 关键优化：预加载点赞和收藏
        if user.is_authenticated:
            from django.db.models import Prefetch
            queryset = queryset.prefetch_related(
                Prefetch(
                    'post_likes',
                    queryset=PostLike.objects.filter(user=user),
                    to_attr='user_likes'
                ),
                Prefetch(
                    'bookmarked_by',
                    queryset=Bookmark.objects.filter(user=user),
                    to_attr='user_bookmarks'
                )
            )
        return queryset

    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        return PostSerializer
    
    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)
        # 更新用户帖子数
        if hasattr(self.request.user, 'profile'):
            profile = self.request.user.profile
            profile.posts_count += 1
            profile.save()
    
    @action(detail=False, methods=['get'])
    def feed(self, request):
        """Feed流 - 支持hot/new/follow排序"""
        tab = request.query_params.get('tab', 'hot')
        queryset = self.get_queryset()
        
        if tab == 'follow':
            # 只显示关注用户的帖子
            if request.user.is_authenticated:
                from apps.social.models import Follow
                following_ids = Follow.objects.filter(
                    follower=request.user
                ).values_list('following_id', flat=True)
                queryset = queryset.filter(author_id__in=following_ids)
        
        elif tab == 'hot':
            # Hot算法: (likes * 2 + comments) / (hours + 2)^1.5
            from django.db.models.functions import Extract, Now

            queryset = queryset.annotate(
               # 正确的方式：使用 Extract(epoch) 把时间转成秒数
              age_seconds=ExpressionWrapper(
                 Extract(Now(), 'epoch') - Extract(F('created_at'), 'epoch'),
                    output_field=FloatField()
                )
        ).annotate(
                # 把秒数转成小时数
                age_hours=ExpressionWrapper(
                    F('age_seconds') / 3600.0,
                    output_field=FloatField()
                )
         ).annotate(
        # 计算热度分数
          hot_score=ExpressionWrapper(
              (F('likes_count') * 2 + F('comments_count')) / 
              functions.Power(F('age_hours') + 2.0, 1.5),
              output_field=FloatField()
            )
          ).order_by('-hot_score', '-created_at')
        
        else:  # new
            queryset = queryset.order_by('-created_at')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'data': serializer.data,
            'error': None
        })
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """点赞/取消点赞（幂等）"""
        post = self.get_object()
        like, created = PostLike.objects.get_or_create(user=request.user, post=post)

        if created:
            post.likes_count = F('likes_count') + 1
            post.save(update_fields=['likes_count'])
            post.refresh_from_db()
            message = 'liked'

            # 创建点赞通知
            create_like_notification(
                sender=request.user,
                post=post
            )
        else:
            like.delete()
            post.likes_count = F('likes_count') - 1
            post.save(update_fields=['likes_count'])
            post.refresh_from_db()
            message = 'unliked'
        
        return Response({
            'data': {
                'action': message,
                'likes_count': post.likes_count
            },
            'error': None
        })
    
    @action(detail=True, methods=['post'])
    def bookmark(self, request, pk=None):
        """收藏/取消收藏（幂等）"""
        post = self.get_object()
        bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)
        
        if created:
            post.bookmarks_count = F('bookmarks_count') + 1
            post.save(update_fields=['bookmarks_count'])
            post.refresh_from_db()
            message = 'bookmarked'
        else:
            bookmark.delete()
            post.bookmarks_count = F('bookmarks_count') - 1
            post.save(update_fields=['bookmarks_count'])
            post.refresh_from_db()
            message = 'unbookmarked'
        
        return Response({
            'data': {
                'action': message,
                'bookmarks_count': post.bookmarks_count
            },
            'error': None
        })
    
    @action(detail=True, methods=['post'], url_path='unlike')
    def unlike(self, request, pk=None):
        """取消点赞（向后兼容，实际调用 like 的幂等逻辑）"""
        return self.like(request, pk)
    
    @action(detail=True, methods=['post'], url_path='unbookmark')
    def unbookmark(self, request, pk=None):
        """取消收藏（向后兼容，实际调用 bookmark 的幂等逻辑）"""
        return self.bookmark(request, pk)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_bookmarks(self, request):
        """获取当前用户的收藏列表"""
        bookmarks = Bookmark.objects.filter(user=request.user).select_related('post')
        post_ids = bookmarks.values_list('post_id', flat=True)
        
        queryset = Post.objects.filter(id__in=post_ids).select_related(
            'author', 'target_university', 'target_school'
        ).prefetch_related('tags').order_by('-created_at')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'data': serializer.data,
            'error': None
        })


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """标签API"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['posts_count', 'name']
    ordering = ['-posts_count']
