from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import University, School, UniversityResource
from .serializers import (
    UniversitySerializer, 
    SchoolSerializer, 
    SchoolDetailSerializer,
    UniversityResourceSerializer
)
from core.pagination import StandardResultsPagination


class UniversityViewSet(viewsets.ReadOnlyModelViewSet):
    """大学列表和详情（只读）"""
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["country", "city"]
    search_fields = ["name", "country", "city"]
    ordering_fields = ["name", "students_count", "created_at"]
    ordering = ["name"]
    lookup_field = "slug"
    pagination_class = StandardResultsPagination
    
    @action(detail=True, methods=['get'], url_path='resources')
    def resources(self, request, slug=None):
        """获取特定大学的资源列表"""
        university = self.get_object()
        queryset = UniversityResource.objects.filter(
            university=university,
            is_active=True
        )
        
        # 支持按类别过滤
        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UniversityResourceSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = UniversityResourceSerializer(queryset, many=True)
        return Response({
            'data': serializer.data,
            'error': None
        })


class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    """学院列表和详情（只读）"""
    queryset = School.objects.select_related("university").all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["university"]
    search_fields = ["name", "university__name"]
    ordering_fields = ["name", "students_count", "created_at"]
    ordering = ["name"]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SchoolDetailSerializer
        return SchoolSerializer

