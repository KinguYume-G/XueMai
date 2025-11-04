"""
认证视图
"""
from rest_framework import status, views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .serializers import RegisterSerializer, UserProfileSerializer, ProfileUpdateSerializer


class RegisterView(views.APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # 生成JWT token
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'data': {
                    'user': UserProfileSerializer(user).data,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                },
                'error': None
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'data': None,
            'error': {
                'code': 'validation_error',
                'message': serializer.errors
            }
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(views.APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'data': {
                    'user': UserProfileSerializer(user).data,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                },
                'error': None
            })
        
        return Response({
            'data': None,
            'error': {
                'code': 'invalid_credentials',
                'message': '用户名或密码错误'
            }
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """获取当前用户信息"""
    return Response({
        'data': UserProfileSerializer(request.user).data,
        'error': None
    })


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """更新个人资料"""
    profile = request.user.profile
    serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'data': UserProfileSerializer(request.user).data,
            'error': None
        })
    
    return Response({
        'data': None,
        'error': {
            'code': 'validation_error',
            'message': serializer.errors
        }
    }, status=status.HTTP_400_BAD_REQUEST)
