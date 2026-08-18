from rest_framework import serializers

from .models import School, University, UniversityResource


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = [
            "id",
            "name",
            "slug",
            "country",
            "city",
            "logo",
            "website",
            "description",
            "students_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["slug", "students_count", "created_at", "updated_at"]


class SchoolSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(source="university.name", read_only=True)

    class Meta:
        model = School
        fields = [
            "id",
            "university",
            "university_name",
            "name",
            "slug",
            "description",
            "students_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["slug", "students_count", "created_at", "updated_at"]


class SchoolDetailSerializer(serializers.ModelSerializer):
    university = UniversitySerializer(read_only=True)

    class Meta:
        model = School
        fields = [
            "id",
            "university",
            "name",
            "slug",
            "description",
            "students_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["slug", "students_count", "created_at", "updated_at"]


class UniversityResourceSerializer(serializers.ModelSerializer):
    """大学资源序列化器"""

    university_name = serializers.CharField(source="university.name", read_only=True)
    category_display = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = UniversityResource
        fields = [
            "id",
            "university",
            "university_name",
            "category",
            "category_display",
            "title",
            "content",
            "extra",
            "is_active",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at"]
