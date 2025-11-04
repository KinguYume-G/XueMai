# Social views
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import F

from .models import Follow
from .serializers import FollowSerializer, FollowActionSerializer
from core.pagination import StandardResultsPagination

User = get_user_model()


class FollowViewSet(viewsets.ReadOnlyModelViewSet):
    """关注关系API"""
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    
    def get_queryset(self):
        """获取当前用户的关注/粉丝列表"""
        user_id = self.request.query_params.get('user_id', self.request.user.id)
        action_type = self.request.query_params.get('type', 'following')
        
        if action_type == 'followers':
            # 获取粉丝
            return Follow.objects.filter(following_id=user_id).select_related('follower', 'following')
        else:
            # 获取关注列表
            return Follow.objects.filter(follower_id=user_id).select_related('follower', 'following')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user(request):
    """关注/取消关注用户（幂等）"""
    serializer = FollowActionSerializer(data=request.data, context={'request': request})
    
    if not serializer.is_valid():
        return Response({
            'data': None,
            'error': {
                'code': 'validation_error',
                'message': serializer.errors
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    target_user_id = serializer.validated_data['user_id']
    target_user = User.objects.get(id=target_user_id)
    
    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=target_user
    )
    
    if created:
        # 更新计数
        if hasattr(request.user, 'profile'):
            request.user.profile.following_count = F('following_count') + 1
            request.user.profile.save(update_fields=['following_count'])
        
        if hasattr(target_user, 'profile'):
            target_user.profile.followers_count = F('followers_count') + 1
            target_user.profile.save(update_fields=['followers_count'])
        
        action = 'followed'
    else:
        follow.delete()
        
        # 更新计数
        if hasattr(request.user, 'profile'):
            request.user.profile.following_count = F('following_count') - 1
            request.user.profile.save(update_fields=['following_count'])
        
        if hasattr(target_user, 'profile'):
            target_user.profile.followers_count = F('followers_count') - 1
            target_user.profile.save(update_fields=['followers_count'])
        
        action = 'unfollowed'
    
    return Response({
        'data': {
            'action': action,
            'user_id': target_user_id
        },
        'error': None
    })
