# User views
# apps/users/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Profile
from .serializers import UserSerializer, ProfileSerializer, ProfileUpdateSerializer


class UserViewSet(viewsets.ModelViewSet):
    """用户API视图集"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "email", "bio"]
    ordering_fields = ["created_at", "username"]
    ordering = ["-created_at"]
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """获取当前用户信息"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class ProfileViewSet(viewsets.ModelViewSet):
    """用户资料API"""
    queryset = Profile.objects.select_related("user", "university", "school").all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["university", "school", "grade"]
    search_fields = ["user__username", "user__email", "major"]
    ordering_fields = ["followers_count", "posts_count", "created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return ProfileUpdateSerializer
        return ProfileSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated()]
        return super().get_permissions()

    def perform_update(self, serializer):
        # 只允许更新自己的资料
        if self.request.user == serializer.instance.user:
            serializer.save()

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        """获取当前登录用户的资料"""
        profile, created = Profile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=["put", "patch"], permission_classes=[IsAuthenticated])
    def update_me(self, request):
        """更新当前登录用户的资料"""
        profile, created = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ProfileSerializer(profile).data)
