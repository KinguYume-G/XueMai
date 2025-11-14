from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Bookmark
from .serializers import BookmarkSerializer


class BookmarkViewSet(viewsets.ModelViewSet):
    """收藏视图集"""
    permission_classes = [IsAuthenticated]
    serializer_class = BookmarkSerializer

    def get_queryset(self):
        """只返回当前用户的收藏"""
        return Bookmark.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """获取收藏列表（可按类型筛选）"""
        content_type = request.query_params.get('type')

        queryset = self.get_queryset()

        if content_type:
            queryset = queryset.filter(content_type=content_type)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """添加收藏"""
        content_type = request.data.get('content_type')
        object_id = request.data.get('object_id')

        # 检查是否已收藏
        existing = Bookmark.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=object_id
        ).first()

        if existing:
            return Response({'detail': '已经收藏过了'}, status=status.HTTP_200_OK)

        # 创建收藏
        bookmark = Bookmark.objects.create(
            user=request.user,
            content_type=content_type,
            object_id=object_id
        )

        serializer = self.get_serializer(bookmark)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """取消收藏"""
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='toggle')
    def toggle(self, request):
        """切换收藏状态（收藏/取消收藏）"""
        content_type = request.data.get('content_type')
        object_id = request.data.get('object_id')

        # 查找是否已收藏
        bookmark = Bookmark.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=object_id
        ).first()

        if bookmark:
            # 已收藏 → 取消收藏
            bookmark.delete()
            return Response({'bookmarked': False}, status=status.HTTP_200_OK)
        else:
            # 未收藏 → 添加收藏
            Bookmark.objects.create(
                user=request.user,
                content_type=content_type,
                object_id=object_id
            )
            return Response({'bookmarked': True}, status=status.HTTP_201_CREATED)
