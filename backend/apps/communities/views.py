# Communities views
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from core.pagination import StandardResultsPagination
from core.permissions import IsOwnerOrStaff, filter_public_or_owned

from .models import Community, CommunityMember
from .serializers import CommunitySerializer


class CommunityViewSet(viewsets.ModelViewSet):
    """
    社区API
    支持筛选参数：category, city, oncampus, study_group
    """

    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrStaff]
    owner_fields = ("created_by",)
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["members", "activity_rate", "created_at"]
    ordering = ["-members", "-activity_rate"]
    lookup_field = "slug"

    def get_queryset(self):
        queryset = filter_public_or_owned(
            super().get_queryset(), self.request.user, "created_by"
        )

        # 筛选参数
        category = self.request.query_params.get("category")
        city = self.request.query_params.get("city")
        oncampus = self.request.query_params.get("oncampus")
        study_group = self.request.query_params.get("study_group")

        if category:
            queryset = queryset.filter(category=category)
        if city:
            queryset = queryset.filter(city=city)
        if oncampus is not None:
            is_oncampus = oncampus.lower() in ["true", "1", "yes"]
            queryset = queryset.filter(is_oncampus=is_oncampus)
        if study_group is not None:
            is_study_group = study_group.lower() in ["true", "1", "yes"]
            queryset = queryset.filter(is_study_group=is_study_group)

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def join(self, request, slug=None):
        """
        加入/退出社区（Toggle设计）
        POST /api/communities/{slug}/join/
        首次调用：加入社区，返回201
        再次调用：退出社区，返回204
        """
        community = self.get_object()
        user = request.user

        membership, created = CommunityMember.objects.get_or_create(user=user, community=community)

        if created:
            # 新加入，增加成员数
            community.members += 1
            community.save(update_fields=["members"])
            return Response(
                {"joined": True, "message": "成功加入社区"}, status=status.HTTP_201_CREATED
            )
        else:
            # 已存在，退出社区
            membership.delete()
            if community.members > 0:
                community.members -= 1
                community.save(update_fields=["members"])
            return Response(
                {"joined": False, "message": "已退出社区"}, status=status.HTTP_204_NO_CONTENT
            )

    @action(detail=True, methods=["delete"], permission_classes=[IsAuthenticated])
    def leave(self, request, slug=None):
        """
        退出社区（显式设计，可选）
        DELETE /api/communities/{slug}/leave/
        """
        community = self.get_object()
        user = request.user

        deleted_count, _ = CommunityMember.objects.filter(user=user, community=community).delete()

        if deleted_count > 0:
            if community.members > 0:
                community.members -= 1
                community.save(update_fields=["members"])
            return Response({"joined": False, "message": "已退出社区"}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"joined": False, "message": "您未加入此社区"}, status=status.HTTP_200_OK
            )
