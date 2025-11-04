# Opportunities serializers
from rest_framework import serializers
from .models import ExchangeProgram, Internship
from apps.users.serializers import UserSerializer


class ExchangeProgramSerializer(serializers.ModelSerializer):
    posted_by_info = UserSerializer(source='posted_by', read_only=True)
    host_university_name = serializers.CharField(source='host_university.name', read_only=True)
    
    class Meta:
        model = ExchangeProgram
        fields = [
            'id', 'title', 'description', 'host_university', 'host_university_name',
            'location', 'duration', 'deadline', 'requirements', 'link',
            'visibility', 'is_published', 'posted_by', 'posted_by_info',
            'views_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['posted_by', 'views_count', 'created_at', 'updated_at']


class InternshipSerializer(serializers.ModelSerializer):
    posted_by_info = UserSerializer(source='posted_by', read_only=True)
    
    class Meta:
        model = Internship
        fields = [
            'id', 'title', 'company', 'description', 'location', 'type',
            'duration', 'deadline', 'requirements', 'salary_range', 'link',
            'visibility', 'is_published', 'posted_by', 'posted_by_info',
            'views_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['posted_by', 'views_count', 'created_at', 'updated_at']
