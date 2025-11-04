from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import AIDocument, AIChunk, AIEmbedding, AIQueryLog
from .serializers import (
    AIDocumentSerializer,
    AIChunkSerializer,
    AIEmbeddingSerializer,
    AIQueryLogSerializer,
    AIQueryRequestSerializer,
    AIQueryResponseSerializer
)
from core.pagination import StandardResultsPagination


class AIDocumentViewSet(viewsets.ModelViewSet):
    """AI文档管理API"""
    queryset = AIDocument.objects.all()
    serializer_class = AIDocumentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['university', 'doc_type', 'is_active']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class AIChunkViewSet(viewsets.ReadOnlyModelViewSet):
    """AI文本块API（只读）"""
    queryset = AIChunk.objects.select_related('document').all()
    serializer_class = AIChunkSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['document']
    ordering = ['document', 'chunk_index']


class AIQueryLogViewSet(viewsets.ReadOnlyModelViewSet):
    """AI查询日志API（只读）"""
    queryset = AIQueryLog.objects.all()
    serializer_class = AIQueryLogSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'university']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """用户只能看到自己的查询记录"""
        if self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def ai_query(request):
    """
    AI查询接口（Mock实现）
    
    POST /api/ai/query/
    {
        "query": "如何申请图书馆卡？",
        "university_id": 1
    }
    """
    serializer = AIQueryRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'data': None,
            'error': {
                'code': 'validation_error',
                'message': serializer.errors
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    query_text = serializer.validated_data['query']
    university_id = serializer.validated_data.get('university_id')
    
    # Mock响应
    mock_response = (
        f"这是一个模拟的 RAG 响应。您的问题是：\"{query_text}\"。\n\n"
        "真实的 RAG 系统将会：\n"
        "1. 使用向量检索找到相关文档\n"
        "2. 调用 LLM (Claude/GPT) 生成回答\n"
        "3. 返回基于校内知识库的准确答案\n\n"
        "当前系统尚未启用。"
    )
    
    # 记录查询日志（如果用户已登录）
    user = request.user if request.user.is_authenticated else None
    AIQueryLog.objects.create(
        user=user,
        query_text=query_text,
        response_text=mock_response,
        university_id=university_id,
        matched_chunks=[],
        response_time_ms=50
    )
    
    response_serializer = AIQueryResponseSerializer({
        'query': query_text,
        'response': mock_response,
        'is_mock': True,
        'matched_chunks': []
    })
    
    return Response({
        'data': response_serializer.data,
        'error': None
    })

