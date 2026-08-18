from rest_framework import serializers

from .models import (  # AIMessage, # 暂时注释掉，因为 AIMessage 模型已不存在
    AIChunk,
    AIConversation,
    AIDocument,
    AIEmbedding,
    AIQueryLog,
)


class AIDocumentSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(source="university.name", read_only=True)
    doc_type_display = serializers.CharField(source="get_doc_type_display", read_only=True)

    class Meta:
        model = AIDocument
        fields = [
            "id",
            "university",
            "university_name",
            "doc_type",
            "doc_type_display",
            "title",
            "content",
            "source_url",
            "metadata",
            "is_active",
            "uploaded_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uploaded_by", "created_at", "updated_at"]


class AIChunkSerializer(serializers.ModelSerializer):
    document_title = serializers.CharField(source="document.title", read_only=True)

    class Meta:
        model = AIChunk
        fields = [
            "id",
            "document",
            "document_title",
            "content",
            "chunk_index",
            "chunk_metadata",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class AIEmbeddingSerializer(serializers.ModelSerializer):
    chunk_content = serializers.CharField(source="chunk.content", read_only=True)

    class Meta:
        model = AIEmbedding
        fields = [
            "id",
            "chunk",
            "chunk_content",
            "embedding_vector",
            "embedding_model",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class AIQueryLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = AIQueryLog
        fields = [
            "id",
            "user",
            "username",
            "query_text",
            "response_text",
            "university",
            "matched_chunks",
            "response_time_ms",
            "is_helpful",
            "feedback_text",
            "created_at",
        ]
        read_only_fields = ["created_at"]


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


# class AIMessageSerializer(serializers.ModelSerializer): # 暂时注释掉
#     """
#     AI 消息记录序列化器。
#
#     用于序列化单条 `AIMessage` 记录。
#     """
#
#     class Meta:
#         model = AIMessage
#         fields = ['id', 'role', 'content', 'tokens', 'model_used', 'created_at']
#         read_only_fields = ['id', 'created_at']


# class AIConversationSerializer(serializers.ModelSerializer): # 暂时注释掉
#     """
#     AI 对话会话序列化器。
#
#     包含嵌套的消息列表与消息数量统计。
#     """
#
#     messages = AIMessageSerializer(many=True, read_only=True)
#     message_count = serializers.SerializerMethodField()
#
#     class Meta:
#         model = AIConversation
#         fields = [
#             'id',
#             'title',
#             'ai_function',
#             'messages',
#             'message_count',
#             'created_at',
#             'updated_at',
#         ]
#         read_only_fields = ['id', 'created_at', 'updated_at', 'message_count']
#
#     def get_message_count(self, obj: AIConversation) -> int:
#         """
#         返回会话下消息数量。
#         """
#         return obj.get_message_count()


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(
        max_length=5000,
        required=True,
        help_text="用户输入的消息内容",
    )
    conversation_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="可选，会话 ID，用于继续之前的对话",
    )
    stream = serializers.BooleanField(
        default=True,
        required=False,
        help_text="是否使用流式响应",
    )
    ai_function = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="可选，指定本次使用的 AI 功能（如：智能对话、简历优化）",
    )
