from rest_framework import serializers
from .models import AIDocument, AIChunk, AIEmbedding, AIQueryLog


class AIDocumentSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(source='university.name', read_only=True)
    doc_type_display = serializers.CharField(source='get_doc_type_display', read_only=True)
    
    class Meta:
        model = AIDocument
        fields = [
            'id', 'university', 'university_name', 'doc_type', 'doc_type_display',
            'title', 'content', 'source_url', 'metadata', 'is_active',
            'uploaded_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['uploaded_by', 'created_at', 'updated_at']


class AIChunkSerializer(serializers.ModelSerializer):
    document_title = serializers.CharField(source='document.title', read_only=True)
    
    class Meta:
        model = AIChunk
        fields = [
            'id', 'document', 'document_title', 'content',
            'chunk_index', 'chunk_metadata', 'created_at'
        ]
        read_only_fields = ['created_at']


class AIEmbeddingSerializer(serializers.ModelSerializer):
    chunk_content = serializers.CharField(source='chunk.content', read_only=True)
    
    class Meta:
        model = AIEmbedding
        fields = [
            'id', 'chunk', 'chunk_content', 'embedding_vector',
            'embedding_model', 'created_at'
        ]
        read_only_fields = ['created_at']


class AIQueryLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AIQueryLog
        fields = [
            'id', 'user', 'username', 'query_text', 'response_text',
            'university', 'matched_chunks', 'response_time_ms',
            'is_helpful', 'feedback_text', 'created_at'
        ]
        read_only_fields = ['created_at']


class AIQueryRequestSerializer(serializers.Serializer):
    """AI查询请求序列化器"""
    query = serializers.CharField(max_length=500, required=True)
    university_id = serializers.IntegerField(required=False, allow_null=True)
    
    
class AIQueryResponseSerializer(serializers.Serializer):
    """AI查询响应序列化器"""
    query = serializers.CharField()
    response = serializers.CharField()
    is_mock = serializers.BooleanField(default=True)
    matched_chunks = serializers.ListField(child=serializers.IntegerField(), required=False)

