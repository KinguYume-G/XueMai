# User serializers
# apps/users/serializers.py
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """用户序列化器（类似前端的Zod验证）"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'avatar', 'bio', 'created_at']
        read_only_fields = ['id', 'created_at']

class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("邮箱已被注册")
        return value