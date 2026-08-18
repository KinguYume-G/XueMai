# Forums views
from datetime import timedelta

from django.db.models import Count, F, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from core.pagination import StandardResultsPagination
from core.permissions import IsOwnerOrStaff, filter_public_or_owned

from .models import Faculty, Forum, Topic
from .serializers import (
    FacultySerializer,
    ForumSerializer,
    TopicCreateSerializer,
    TopicSerializer,
)


@api_view(["GET"])
@permission_classes([AllowAny])
def forum_overview(request):
    """
    论坛概览统计
    GET /api/forums/overview/
    """
    visible_topics = filter_public_or_owned(Topic.objects.all(), request.user, "author")
    data = {
        "faculty_count": Faculty.objects.count(),
        "major_count": Faculty.objects.aggregate(
            total=Coalesce(Sum("major_count"), 0)
        )["total"],
        "active_posts": visible_topics.count(),
        "active_users": visible_topics.values("author_id").distinct().count(),
    }
    return Response(data)


@api_view(["GET"])
@permission_classes([AllowAny])
def hot_topics(request):
    """
    热门话题统计
    GET /api/topics/hot/?limit=4&window=7d
    """
    try:
        limit = max(1, min(int(request.query_params.get("limit", 4)), 50))
    except (TypeError, ValueError):
        limit = 4

    window = request.query_params.get("window", "7d").lower()
    window_days = {"1d": 1, "7d": 7, "30d": 30, "90d": 90}
    topics = filter_public_or_owned(Topic.objects.all(), request.user, "author")
    if window != "all":
        days = window_days.get(window, 7)
        topics = topics.filter(created_at__gte=timezone.now() - timedelta(days=days))

    data = list(
        topics.filter(tags__isnull=False)
        .values(name=F("tags__name"))
        .annotate(post_count=Count("id", distinct=True))
        .order_by("-post_count", "name")[:limit]
    )
    return Response(data)


class FacultyViewSet(viewsets.ReadOnlyModelViewSet):
    """学院API"""

    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"


class ForumViewSet(viewsets.ReadOnlyModelViewSet):
    """论坛API"""

    queryset = Forum.objects.all()
    serializer_class = ForumSerializer
    permission_classes = [AllowAny]


class TopicViewSet(viewsets.ModelViewSet):
    """话题API"""

    queryset = Topic.objects.select_related("forum", "author").prefetch_related("tags").all()
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrStaff]
    owner_fields = ("author",)
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["forum", "author", "is_solved"]
    search_fields = ["title", "content"]
    ordering_fields = ["created_at", "views_count", "replies_count"]
    ordering = ["-is_pinned", "-updated_at"]

    def get_queryset(self):
        return filter_public_or_owned(
            super().get_queryset(), self.request.user, "author"
        )

    def get_permissions(self):
        """允许匿名用户查看列表和详情"""
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return TopicCreateSerializer
        return TopicSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """获取详情时增加浏览数"""
        instance = self.get_object()
        instance.views_count = F("views_count") + 1
        instance.save(update_fields=["views_count"])
        instance.refresh_from_db()

        serializer = self.get_serializer(instance)
        return Response({"data": serializer.data, "error": None})
