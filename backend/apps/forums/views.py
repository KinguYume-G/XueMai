# Forums views
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F, Count, Sum

from .models import Forum, Topic, Faculty
from .serializers import ForumSerializer, TopicSerializer, TopicCreateSerializer, FacultySerializer
from core.pagination import StandardResultsPagination


@api_view(['GET'])
@permission_classes([AllowAny])
def forum_overview(request):
    """
    论坛概览统计
    GET /api/forums/overview/
    """
    data = {
        "faculty_count": Faculty.objects.count(),
        "major_count": Faculty.objects.aggregate(total=Sum('major_count'))['total'] or 0,
        "active_posts": Topic.objects.count(),
        "active_users": Topic.objects.values('author_id').distinct().count(),
    }
    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def hot_topics(request):
    """
    热门话题统计
    GET /api/topics/hot/?limit=4&window=7d
    """
    limit = int(request.query_params.get('limit', 4))
    tags = (
        Topic.tags.through.objects.values('tag__name')
        .annotate(post_count=Count('topic_id'))
        .order_by('-post_count', 'tag__name')[:limit]
    )
    return Response([
        {'name': item['tag__name'], 'post_count': item['post_count']}
        for item in tags
    ])


class FacultyViewSet(viewsets.ReadOnlyModelViewSet):
    """学院API"""
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'


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
