# Comments admin
from django.contrib import admin

from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "author",
        "post",
        "content_preview",
        "parent",
        "likes_count",
        "created_at",
    ]
    list_filter = ["created_at"]
    search_fields = ["content", "author__username", "post__title"]
    raw_id_fields = ["author", "post", "parent"]
    readonly_fields = ["likes_count", "created_at"]

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "内容预览"
