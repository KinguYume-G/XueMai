# Notifications admin
from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "type", "title", "is_read", "created_at"]
    list_filter = ["type", "is_read", "created_at"]
    search_fields = ["user__username", "title", "content"]
    raw_id_fields = ["user"]
    readonly_fields = ["created_at"]
