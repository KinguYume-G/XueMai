# Communities serializers
from rest_framework import serializers
from .models import Community, CommunityMember


class CommunitySerializer(serializers.ModelSerializer):
    """Community serializer"""
    joined = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = [
            'id', 'name', 'slug', 'description', 'cover_url',
            'category', 'city', 'is_oncampus', 'is_study_group',
            'members', 'activity_rate', 'joined',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'members']

    def get_joined(self, obj):
        """Check if current user has joined"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CommunityMember.objects.filter(
                user=request.user,
                community=obj
            ).exists()
        return False


class CommunityMemberSerializer(serializers.ModelSerializer):
    """Community member serializer"""
    community_name = serializers.CharField(source='community.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = CommunityMember
        fields = ['id', 'user', 'username', 'community', 'community_name', 'joined_at']
        read_only_fields = ['joined_at']
