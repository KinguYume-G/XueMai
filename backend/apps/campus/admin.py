from django.contrib import admin

from .models import School, University, UniversityResource


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ["name", "country", "city", "students_count", "created_at"]
    list_filter = ["country", "city"]
    search_fields = ["name", "country", "city"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at"]


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ["name", "university", "students_count", "created_at"]
    list_filter = ["university"]
    search_fields = ["name", "university__name"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at"]


@admin.register(UniversityResource)
class UniversityResourceAdmin(admin.ModelAdmin):
    list_display = ["title", "university", "category", "is_active", "created_at"]
    list_filter = ["university", "category", "is_active"]
    search_fields = ["title", "content", "university__name"]
    readonly_fields = ["created_by", "created_at", "updated_at"]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
