# Opportunities views
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import ExchangeProgram, Internship
from .serializers import ExchangeProgramSerializer, InternshipSerializer
from core.pagination import StandardResultsPagination


class ExchangeProgramViewSet(viewsets.ModelViewSet):
    """交换项目API"""
    queryset = ExchangeProgram.objects.filter(is_published=True).select_related(
        'host_university', 'posted_by'
    )
    serializer_class = ExchangeProgramSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['host_university', 'visibility']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['created_at', 'deadline', 'views_count']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """允许匿名用户查看列表和详情"""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class InternshipViewSet(viewsets.ModelViewSet):
    """实习机会API"""
    queryset = Internship.objects.filter(is_published=True).select_related('posted_by')
    serializer_class = InternshipSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'visibility', 'company']
    search_fields = ['title', 'company', 'description', 'location']
    ordering_fields = ['created_at', 'deadline', 'views_count']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """允许匿名用户查看列表和详情"""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)
