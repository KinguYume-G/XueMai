# Opportunities admin
from django.contrib import admin
from .models import ExchangeProgram, Internship


@admin.register(ExchangeProgram)
class ExchangeProgramAdmin(admin.ModelAdmin):
    list_display = ['title', 'host_university', 'location', 'deadline', 
                    'visibility', 'is_published', 'views_count', 'created_at']
    list_filter = ['visibility', 'is_published', 'host_university', 'created_at']
    search_fields = ['title', 'description', 'location']
    raw_id_fields = ['host_university', 'posted_by']
    readonly_fields = ['views_count', 'created_at', 'updated_at']


@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'type', 'location', 'deadline',
                    'visibility', 'is_published', 'views_count', 'created_at']
    list_filter = ['type', 'visibility', 'is_published', 'created_at']
    search_fields = ['title', 'company', 'description', 'location']
    raw_id_fields = ['posted_by']
    readonly_fields = ['views_count', 'created_at', 'updated_at']
