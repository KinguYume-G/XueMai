"""
认证相关序列化器
"""

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework import serializers

from apps.users.models import Profile
from apps.users.serializers import ProfileSerializer

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, allow_blank=False)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password_confirm"]

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password": "密码不匹配"})
        return data

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("该邮箱已被注册。")
        return email

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        try:
            with transaction.atomic():
                user = User.objects.create_user(**validated_data)
        except IntegrityError as exc:
            # The database constraint is the final guard against concurrent
            # registrations that pass validation at the same time.
            if User.objects.filter(
                email__iexact=validated_data["email"]
            ).exists():
                raise serializers.ValidationError(
                    {"email": ["该邮箱已被注册。"]}
                ) from exc
            raise
        # 自动创建Profile (signals会处理)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "profile", "date_joined"]
        read_only_fields = ["id", "date_joined"]

    def get_profile(self, obj):
        if hasattr(obj, "profile"):
            return ProfileSerializer(obj.profile).data
        return None


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "university",
            "school",
            "major",
            "grade",
            "bio",
            "followers_count",
            "following_count",
            "posts_count",
            "github_url",
            "linkedin_url",
            "website",
        ]
        read_only_fields = ["followers_count", "following_count", "posts_count"]


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "university",
            "school",
            "major",
            "grade",
            "bio",
            "github_url",
            "linkedin_url",
            "website",
        ]
