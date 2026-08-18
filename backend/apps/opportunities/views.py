# Opportunities views
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from core.pagination import StandardResultsPagination
from core.permissions import IsOwnerOrStaff, filter_public_or_owned

from .models import ExchangeProgram, Internship, Startup
from .serializers import (
    ExchangeProgramSerializer,
    InternshipSerializer,
    StartupSerializer,
)


class ExchangeProgramViewSet(viewsets.ModelViewSet):
    """
    交换项目API
    支持筛选：country, university, deadline_before, deadline_after
    支持排序：deadline, -deadline, -rating_avg, -applied_count
    """

    queryset = ExchangeProgram.objects.select_related(
        "host_university", "posted_by"
    )
    serializer_class = ExchangeProgramSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrStaff]
    owner_fields = ("posted_by",)
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["host_university", "visibility", "country"]
    search_fields = ["title", "description", "location"]
    ordering_fields = ["created_at", "deadline", "views_count", "rating_avg", "applied_count"]
    ordering = ["deadline"]  # 默认按截止日期升序

    def get_queryset(self):
        queryset = filter_public_or_owned(
            super().get_queryset(), self.request.user, "posted_by"
        )

        # 筛选参数
        university = self.request.query_params.get("university")
        deadline_before = self.request.query_params.get("deadline_before")
        deadline_after = self.request.query_params.get("deadline_after")

        if university:
            queryset = queryset.filter(host_university__name__icontains=university)
        if deadline_before:
            queryset = queryset.filter(deadline__lte=deadline_before)
        if deadline_after:
            queryset = queryset.filter(deadline__gte=deadline_after)

        # 默认只显示未截止的项目
        if not deadline_before and not deadline_after and not self.request.user.is_staff:
            deadline_filter = Q(deadline__gte=timezone.now().date())
            if self.request.user.is_authenticated:
                deadline_filter |= Q(posted_by=self.request.user)
            queryset = queryset.filter(deadline_filter)

        return queryset

    def get_permissions(self):
        """允许匿名用户查看列表和详情"""
        if self.action in ["list", "retrieve", "upcoming"]:
            return [AllowAny()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)

    @action(detail=False, methods=["get"], url_path="upcoming")
    def upcoming(self, request):
        """
        即将截止的交换项目
        GET /api/exchange_programs/upcoming/?limit=2
        """
        limit = int(request.query_params.get("limit", 2))
        today = timezone.now().date()

        programs = (
            filter_public_or_owned(
                ExchangeProgram.objects.all(), request.user, "posted_by"
            )
            .filter(deadline__gte=today)
            .select_related("host_university")
            .order_by("deadline")[:limit]
        )

        # 返回最小字段集
        data = [
            {
                "id": p.id,
                "title": p.title,
                "university": p.host_university.name if p.host_university else "",
                "country": p.country or "",
                "deadline": p.deadline,
                "cover_url": p.cover_url or "",
            }
            for p in programs
        ]

        return Response(data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def bookmark(self, request, pk=None):
        """
        收藏/取消收藏交换项目（Toggle设计）
        POST /api/exchange_programs/{id}/bookmark/
        TODO: Implement with generic bookmark model
        """
        from apps.bookmarks.models import Bookmark

        program = self.get_object()
        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            content_type="exchange",
            object_id=program.pk,
        )
        if not created:
            bookmark.delete()
        return Response(
            {"bookmarked": created},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class InternshipViewSet(viewsets.ModelViewSet):
    """
    实习机会API
    支持筛选：country, city, remote, tag
    """

    queryset = Internship.objects.select_related("posted_by")
    serializer_class = InternshipSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrStaff]
    owner_fields = ("posted_by",)
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["type", "visibility", "company", "country", "city", "remote"]
    search_fields = ["title", "company", "description", "location"]
    ordering_fields = ["created_at", "deadline", "views_count", "applicants_count"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = filter_public_or_owned(
            super().get_queryset(), self.request.user, "posted_by"
        )
        # 支持tag筛选 (JSON字段)
        tag = self.request.query_params.get("tag")
        if tag:
            queryset = queryset.filter(skills__contains=[tag])
        return queryset

    def get_permissions(self):
        """允许匿名用户查看列表和详情"""
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def bookmark(self, request, pk=None):
        """收藏/取消收藏实习。"""
        from apps.bookmarks.models import Bookmark

        internship = self.get_object()
        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            content_type="internship",
            object_id=internship.pk,
        )
        if not created:
            bookmark.delete()
        return Response(
            {"bookmarked": created},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class StartupViewSet(viewsets.ModelViewSet):
    """
    创业机会API
    支持筛选：city, tag
    """

    queryset = Startup.objects.select_related("posted_by")
    serializer_class = StartupSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrStaff]
    owner_fields = ("posted_by",)
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["city", "country", "visibility", "is_published"]
    search_fields = ["title", "org_name", "description"]
    ordering_fields = ["created_at", "followers_count"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = filter_public_or_owned(
            super().get_queryset(), self.request.user, "posted_by"
        )
        # 支持tag筛选 (JSON字段)
        tag = self.request.query_params.get("tag")
        if tag:
            queryset = queryset.filter(tags__contains=[tag])
        return queryset

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)
