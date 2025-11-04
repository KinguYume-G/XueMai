# Users serializers
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile

GRADE_MAP = {
    1: "freshman",
    2: "sophomore",
    3: "junior",
    4: "senior",
}
GRADE_REVERSE_MAP = {v: k for k, v in GRADE_MAP.items()}

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """基础用户序列化器"""

    class Meta:
        model = User
        fields = ["id", "username", "email", "bio", "created_at"]
        read_only_fields = ["id", "created_at"]


class ProfileSerializer(serializers.ModelSerializer):
    """用户资料序列化器"""

    university_name = serializers.CharField(source="university.name", read_only=True)
    school_name = serializers.CharField(source="school.name", read_only=True)
    grade = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "university",
            "university_name",
            "school",
            "school_name",
            "avatar_url",
            "major",
            "grade",
            "bio",
            "github_url",
            "linkedin_url",
            "website",
            "followers_count",
            "following_count",
            "posts_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "followers_count",
            "following_count",
            "posts_count",
            "created_at",
            "updated_at",
        ]

    def get_grade(self, obj):
        if not obj.grade:
            return None
        if obj.grade in GRADE_REVERSE_MAP:
            return GRADE_REVERSE_MAP[obj.grade]
        return obj.grade


class UserDetailSerializer(serializers.ModelSerializer):
    """详细用户序列化器（含profile）"""

    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "bio", "profile", "created_at"]
        read_only_fields = ["id", "created_at"]


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """用于更新用户资料的序列化器"""

    class Meta:
        model = Profile
        fields = ["university", "avatar_url", "school", "grade", "major", "bio"]

    def validate_grade(self, value):
        if value in (None, "", 0, "0"):
            return ""

        try:
            grade_int = int(value)
        except (TypeError, ValueError):
            raise serializers.ValidationError("年级必须在1-4之间") from None

        if grade_int not in GRADE_MAP:
            raise serializers.ValidationError("年级必须在1-4之间")

        return GRADE_MAP[grade_int]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        grade_value = data.get("grade")
        if grade_value in GRADE_REVERSE_MAP:
            data["grade"] = GRADE_REVERSE_MAP[grade_value]
        elif not grade_value:
            data["grade"] = None
        return data
