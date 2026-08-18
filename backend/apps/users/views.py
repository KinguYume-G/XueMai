# User views
# apps/users/views.py
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from core.permissions import IsOwnerOrStaff

from .models import Profile, User
from .serializers import (
    ProfileSerializer,
    ProfileUpdateSerializer,
    UserDetailSerializer,
    UserPrivateSerializer,
    UserPublicSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    """用户API视图集"""

    # ✅ 优化：预加载 profile，避免 N+1 查询
    queryset = User.objects.select_related("profile").all()
    serializer_class = UserPrivateSerializer  # Default for authenticated users
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrStaff]
    owner_fields = ()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ["created_at", "username"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """根据认证状态返回不同的序列化器"""
        if not self.request.user.is_authenticated:
            return UserPublicSerializer
        # Detail view (e.g. /users/{id}/, user profile page) needs the
        # embedded profile (avatar/major/university/follow counts) —
        # UserPrivateSerializer omits it entirely, which left profile pages
        # rendering almost nothing for every viewer.
        if self.action == "retrieve":
            return UserDetailSerializer
        return UserPrivateSerializer

    def get_search_fields(self):
        """未认证用户不能通过 email/bio 搜索"""
        if self.request.user.is_authenticated:
            return ["username", "email", "bio"]
        return ["username"]  # 仅允许搜索用户名

    @property
    def search_fields(self):
        """动态返回搜索字段"""
        return self.get_search_fields()

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        """获取当前用户信息"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class ProfileViewSet(viewsets.ModelViewSet):
    """用户资料API"""

    queryset = Profile.objects.select_related("user", "university", "school").all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrStaff]
    owner_fields = ("user",)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["university", "school", "grade"]
    ordering_fields = ["followers_count", "posts_count", "created_at"]
    ordering = ["-created_at"]

    def get_search_fields(self):
        """未认证用户不能通过 email 搜索"""
        if self.request.user.is_authenticated:
            return ["user__username", "user__email", "major"]
        return ["user__username", "major"]  # 移除 email 搜索

    @property
    def search_fields(self):
        """动态返回搜索字段"""
        return self.get_search_fields()

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return ProfileUpdateSerializer
        return ProfileSerializer

    def perform_update(self, serializer):
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
