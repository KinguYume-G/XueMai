# Communities admin
from django.contrib import admin
from .models import Community, CommunityMember


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'category', 'city', 'members', 'activity_rate', 'created_at']
    list_filter = ['category', 'is_oncampus', 'is_study_group', 'created_at']
    search_fields = ['name', 'description', 'city']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CommunityMember)
class CommunityMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'community', 'joined_at']
    list_filter = ['community', 'joined_at']
    search_fields = ['user__username', 'community__name']
    raw_id_fields = ['user', 'community']
