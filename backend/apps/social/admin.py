# Social admin
from django.contrib import admin
from .models import Follow, Like


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'created_at']
    list_filter = ['created_at']
    search_fields = ['follower__username', 'following__username']
    raw_id_fields = ['follower', 'following']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_target', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username']
    raw_id_fields = ['user', 'post', 'comment']
    
    def get_target(self, obj):
        if obj.post:
            return f"Post: {obj.post.title[:30]}"
        return f"Comment: {obj.comment.content[:30]}"
    get_target.short_description = '目标'
