# Social serializers
from rest_framework import serializers
from .models import Follow, Like
from apps.users.serializers import UserSerializer


class FollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['created_at']


class FollowActionSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    
    def validate_user_id(self, value):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("用户不存在")
        
        # 不能关注自己
        request = self.context.get('request')
        if request and request.user.id == value:
            raise serializers.ValidationError("不能关注自己")
        
        return value
