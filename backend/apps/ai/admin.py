from django.contrib import admin
from .models import AIDocument, AIChunk, AIEmbedding, AIQueryLog


@admin.register(AIDocument)
class AIDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'doc_type', 'university', 'is_active', 'created_at']
    list_filter = ['doc_type', 'university', 'is_active']
    search_fields = ['title', 'content']
    readonly_fields = ['uploaded_by', 'created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AIChunk)
class AIChunkAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'document', 'chunk_index', 'created_at']
    list_filter = ['document__doc_type']
    search_fields = ['content', 'document__title']
    readonly_fields = ['created_at']


@admin.register(AIEmbedding)
class AIEmbeddingAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'embedding_model', 'created_at']
    list_filter = ['embedding_model']
    readonly_fields = ['created_at']


@admin.register(AIQueryLog)
class AIQueryLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'query_text_short', 'university', 'is_helpful', 'created_at']
    list_filter = ['is_helpful', 'university', 'created_at']
    search_fields = ['query_text', 'response_text', 'user__username']
    readonly_fields = ['created_at']
    
    def query_text_short(self, obj):
        return obj.query_text[:50] + '...' if len(obj.query_text) > 50 else obj.query_text
    query_text_short.short_description = '查询文本'

