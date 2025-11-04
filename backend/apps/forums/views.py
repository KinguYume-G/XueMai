# Forums views
from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F

from .models import Forum, Topic
from .serializers import ForumSerializer, TopicSerializer, TopicCreateSerializer
from core.pagination import StandardResultsPagination


class ForumViewSet(viewsets.ReadOnlyModelViewSet):
    """论坛API"""
    queryset = Forum.objects.all()
    serializer_class = ForumSerializer
    permission_classes = [AllowAny]


class TopicViewSet(viewsets.ModelViewSet):
    """话题API"""
    queryset = Topic.objects.select_related('forum', 'author').prefetch_related('tags').all()
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['forum', 'author', 'is_solved']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'views_count', 'replies_count']
    ordering = ['-is_pinned', '-updated_at']
    
    def get_permissions(self):
        """允许匿名用户查看列表和详情"""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return super().get_permissions()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TopicCreateSerializer
        return TopicSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        """获取详情时增加浏览数"""
        instance = self.get_object()
        instance.views_count = F('views_count') + 1
        instance.save(update_fields=['views_count'])
        instance.refresh_from_db()
        
        serializer = self.get_serializer(instance)
        return Response({
            'data': serializer.data,
            'error': None
        })
