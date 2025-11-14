# Social admin
from django.contrib import admin
from .models import (
    Follow, Like, FriendRequest, ChatGroup,
    GroupMember, ChatMessage, UserOnlineStatus
)


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


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['from_user__username', 'to_user__username']
    raw_id_fields = ['from_user', 'to_user']
    actions = ['accept_requests', 'reject_requests']

    def accept_requests(self, request, queryset):
        for req in queryset.filter(status='pending'):
            req.accept()
        self.message_user(request, f"已接受 {queryset.count()} 个好友申请")
    accept_requests.short_description = "接受选中的好友申请"

    def reject_requests(self, request, queryset):
        for req in queryset.filter(status='pending'):
            req.reject()
        self.message_user(request, f"已拒绝 {queryset.count()} 个好友申请")
    reject_requests.short_description = "拒绝选中的好友申请"


@admin.register(ChatGroup)
class ChatGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'creator', 'member_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description', 'creator__username']
    raw_id_fields = ['creator']


@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'group', 'role', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['user__username', 'group__name']
    raw_id_fields = ['user', 'group']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'get_recipient', 'message_type', 'is_read', 'created_at']
    list_filter = ['message_type', 'is_read', 'created_at']
    search_fields = ['from_user__username', 'to_user__username', 'content']
    raw_id_fields = ['from_user', 'to_user', 'group']

    def get_recipient(self, obj):
        if obj.to_user:
            return f"User: {obj.to_user.username}"
        return f"Group: {obj.group.name}"
    get_recipient.short_description = '接收者'


@admin.register(UserOnlineStatus)
class UserOnlineStatusAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_online', 'last_seen', 'status_text']
    list_filter = ['is_online']
    search_fields = ['user__username', 'status_text']
    raw_id_fields = ['user']
