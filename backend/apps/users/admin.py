# Users admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Profile, User


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "用户资料"
    fk_name = "user"
    raw_id_fields = ["university", "school"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ["username", "email", "is_staff", "is_active", "created_at"]
    list_filter = ["is_staff", "is_active", "created_at"]
    fieldsets = BaseUserAdmin.fieldsets + (
        ("额外信息", {"fields": ("bio", "avatar", "created_at", "updated_at")}),
    )
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "university",
        "school",
        "major",
        "grade",
        "followers_count",
        "following_count",
        "posts_count",
    ]
    list_filter = ["grade", "university", "school"]
    search_fields = ["user__username", "user__email", "major"]
    raw_id_fields = ["user", "university", "school"]
    readonly_fields = [
        "followers_count",
        "following_count",
        "posts_count",
        "created_at",
        "updated_at",
    ]
