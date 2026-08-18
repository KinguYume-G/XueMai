"""
认证视图
"""

import logging

from django.contrib.auth import get_user_model
from rest_framework import status, views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    ProfileUpdateSerializer,
    RegisterSerializer,
    UserProfileSerializer,
)

User = get_user_model()
logger = logging.getLogger(__name__)


class RegisterView(views.APIView):
    """
    用户注册视图
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "data": None,
                    "error": {
                        "code": "validation_error",
                        "message": serializer.errors,
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.save()

        # 生成 JWT token
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "data": {
                    "user": UserProfileSerializer(user).data,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                "error": None,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(views.APIView):
    """
    用户登录视图（邮箱 + 密码）
    """

    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        # 1. 基本参数校验
        if not email or not password:
            return Response(
                {
                    "data": None,
                    "error": {
                        "code": "missing_credentials",
                        "message": "邮箱和密码为必填项",
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2. 根据邮箱查找用户（忽略大小写，去除空格）
        try:
            user = User.objects.get(email__iexact=email.strip())
        except User.DoesNotExist:
            user = None
        except User.MultipleObjectsReturned:
            # Older databases may predate the case-insensitive email
            # constraint. Fail closed instead of selecting an account.
            logger.error("Multiple accounts found for one login email")
            user = None

        # 3. 校验密码和账户状态
        if not user or not user.check_password(password) or not user.is_active:
            return Response(
                {
                    "data": None,
                    "error": {
                        "code": "invalid_credentials",
                        "message": "邮箱或密码错误",
                    },
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # 4. 成功登录，签发 JWT
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "data": {
                    "user": UserProfileSerializer(user).data,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                "error": None,
            },
            status=status.HTTP_200_OK,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """获取当前用户信息"""
    return Response(
        {
            "data": UserProfileSerializer(request.user).data,
            "error": None,
        }
    )


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """更新个人资料"""
    profile = request.user.profile
    serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True)

    if not serializer.is_valid():
        return Response(
            {
                "data": None,
                "error": {
                    "code": "validation_error",
                    "message": serializer.errors,
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer.save()
    return Response(
        {
            "data": UserProfileSerializer(request.user).data,
            "error": None,
        }
    )
