# Notifications views
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Notification
from .serializers import NotificationSerializer
from core.pagination import StandardResultsPagination


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """通知API"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_read', 'type']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """只返回当前用户的通知"""
        queryset = Notification.objects.filter(user=self.request.user)
        
        # 支持只看未读
        unread_only = self.request.query_params.get('unread_only', 'false').lower() == 'true'
        if unread_only:
            queryset = queryset.filter(is_read=False)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """列表响应中包含未读数量统计"""
        from django.db.models import Count

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        # 获取所有未读通知
        unread_notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        )

        # 总未读数量
        total_unread = unread_notifications.count()

        # 按类型统计未读数量
        type_counts = unread_notifications.values('type').annotate(
            count=Count('id')
        )

        counts_by_type = {
            'like': 0,
            'comment': 0,
            'follow': 0,
            'system': 0,
        }

        for item in type_counts:
            type_key = item['type'].lower()
            if type_key in counts_by_type:
                counts_by_type[type_key] = item['count']

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['unread_count'] = total_unread
            response.data['counts_by_type'] = counts_by_type
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'data': serializer.data,
            'unread_count': total_unread,
            'counts_by_type': counts_by_type,
            'error': None
        })
    
    @action(detail=False, methods=['post'])
    def read(self, request):
        """标记指定通知为已读"""
        ids = request.data.get('ids', [])
        if not isinstance(ids, list):
            return Response({
                'data': None,
                'error': {
                    'code': 'invalid_input',
                    'message': 'ids必须是数组'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        updated = Notification.objects.filter(
            id__in=ids,
            user=request.user
        ).update(is_read=True)
        
        return Response({
            'data': {'updated_count': updated},
            'error': None
        })
    
    @action(detail=False, methods=['post'])
    def read_all(self, request):
        """标记所有通知为已读"""
        updated = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)
        
        return Response({
            'data': {'updated_count': updated},
            'error': None
        })
    
    @action(detail=False, methods=['post'], url_path='mark_all_as_read')
    def mark_all_as_read(self, request):
        """标记所有通知为已读（别名，向后兼容）"""
        return self.read_all(request)
    
    @action(detail=False, methods=['get'], url_path='unread_count')
    def unread_count(self, request):
        """获取未读通知数量（按类型统计）"""
        from django.db.models import Count

        # 获取所有未读通知
        unread_notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        )

        # 总未读数量
        total_count = unread_notifications.count()

        # 按类型统计
        type_counts = unread_notifications.values('type').annotate(
            count=Count('id')
        )

        # 转换为字典格式
        by_type = {
            'like': 0,
            'comment': 0,
            'follow': 0,
            'system': 0,
        }

        for item in type_counts:
            type_key = item['type'].lower()
            if type_key in by_type:
                by_type[type_key] = item['count']

        return Response({
            'data': {
                'total': total_count,
                'by_type': by_type,
                # 向后兼容
                'unread_count': total_count,
            },
            'error': None
        })
    
    @action(detail=True, methods=['post'], url_path='mark_as_read')
    def mark_as_read(self, request, pk=None):
        """标记单条通知为已读"""
        notification = self.get_object()
        
        if notification.user != request.user:
            return Response({
                'data': None,
                'error': {
                    'code': 'permission_denied',
                    'message': '无权操作此通知'
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        
        return Response({
            'data': {'status': 'success'},
            'error': None
        })
    
    @action(detail=False, methods=['delete'], url_path='clear_all')
    def clear_all(self, request):
        """清空当前用户的所有通知"""
        deleted_count, _ = Notification.objects.filter(user=request.user).delete()
        
        return Response({
            'data': {'deleted_count': deleted_count},
            'error': None
        })
