# Forums admin
from django.contrib import admin
from .models import Forum, Topic


@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name', 'description']


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'forum', 'author', 'views_count', 'replies_count', 
                    'is_pinned', 'is_solved', 'created_at']
    list_filter = ['forum', 'is_pinned', 'is_solved', 'created_at']
    search_fields = ['title', 'content']
    raw_id_fields = ['author', 'forum']
    filter_horizontal = ['tags']

