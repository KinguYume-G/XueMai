from django.contrib import admin

from .models import (
    AIChunk,
    AIConversation,
    AIDocument,
    AIEmbedding,
    AIMessage,
    AIQueryLog,
    AIRoutingLog,
)


@admin.register(AIDocument)
class AIDocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "doc_type", "university", "is_active", "created_at"]
    list_filter = ["doc_type", "university", "is_active"]
    search_fields = ["title", "content"]
    readonly_fields = ["uploaded_by", "created_at", "updated_at"]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AIChunk)
class AIChunkAdmin(admin.ModelAdmin):
    list_display = ["__str__", "document", "chunk_index", "created_at"]
    list_filter = ["document__doc_type"]
    search_fields = ["content", "document__title"]
    readonly_fields = ["created_at"]


@admin.register(AIEmbedding)
class AIEmbeddingAdmin(admin.ModelAdmin):
    list_display = ["__str__", "embedding_model", "created_at"]
    list_filter = ["embedding_model"]
    readonly_fields = ["created_at"]


@admin.register(AIQueryLog)
class AIQueryLogAdmin(admin.ModelAdmin):
    list_display = ["user", "query_text_short", "university", "is_helpful", "created_at"]
    list_filter = ["is_helpful", "university", "created_at"]
    search_fields = ["query_text", "response_text", "user__username"]
    readonly_fields = ["created_at"]

    def query_text_short(self, obj):
        return obj.query_text[:50] + "..." if len(obj.query_text) > 50 else obj.query_text

    query_text_short.short_description = "查询文本"


@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display = ["user", "title", "ai_function", "total_tokens", "created_at"]
    list_filter = ["ai_function", "created_at", "user"]
    search_fields = ["title", "ai_function", "user__username"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(AIMessage)
class AIMessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'role', 'content_short', 'model_used', 'tokens', 'created_at']
    list_filter = ['role', 'model_used', 'created_at']
    search_fields = ['content', 'conversation__title', 'conversation__user__username']
    readonly_fields = ['created_at']

    def content_short(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    content_short.short_description = '内容'


@admin.register(AIRoutingLog)
class AIRoutingLogAdmin(admin.ModelAdmin):
    list_display = ['query_short', 'recognized_function', 'confidence', 'method', 'is_correct', 'created_at']
    list_filter = ['recognized_function', 'method', 'is_correct', 'created_at']
    search_fields = ['query', 'reasoning']
    readonly_fields = ['created_at']

    def query_short(self, obj):
        return obj.query[:40] + '...' if len(obj.query) > 40 else obj.query

    query_short.short_description = '查询'
