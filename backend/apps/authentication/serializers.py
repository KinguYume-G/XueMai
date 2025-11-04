"""
认证相关序列化器
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.users.models import Profile
from apps.users.serializers import ProfileSerializer

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "密码不匹配"})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        # 自动创建Profile (signals会处理)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile', 'date_joined']
        read_only_fields = ['id', 'date_joined']
    
    def get_profile(self, obj):
        if hasattr(obj, 'profile'):
            return ProfileSerializer(obj.profile).data
        return None


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['university', 'school', 'major', 'grade', 'bio', 
                  'followers_count', 'following_count', 'posts_count',
                  'github_url', 'linkedin_url', 'website']
        read_only_fields = ['followers_count', 'following_count', 'posts_count']


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['university', 'school', 'major', 'grade', 'bio',
                  'github_url', 'linkedin_url', 'website']
