# Opportunities serializers
from rest_framework import serializers

from apps.users.serializers import UserPublicSerializer

from .models import ExchangeProgram, Internship, Startup


class ExchangeProgramSerializer(serializers.ModelSerializer):
    posted_by_info = UserPublicSerializer(source="posted_by", read_only=True)
    university = serializers.CharField(source="host_university.name", read_only=True)
    bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = ExchangeProgram
        fields = [
            "id",
            "title",
            "description",
            "host_university",
            "university",
            "location",
            "duration",
            "deadline",
            "requirements",
            "link",
            "cover_url",
            "tuition",
            "stipend",
            "gpa_min",
            "lang_req",
            "country",
            "rating_avg",
            "rating_count",
            "applied_count",
            "website",
            "is_urgent",
            "visibility",
            "is_published",
            "posted_by",
            "posted_by_info",
            "views_count",
            "bookmarked",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "posted_by",
            "views_count",
            "rating_avg",
            "rating_count",
            "applied_count",
            "created_at",
            "updated_at",
        ]

    def get_bookmarked(self, obj):
        """Check if current user has bookmarked"""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            from apps.bookmarks.models import Bookmark

            return Bookmark.objects.filter(
                user=request.user,
                content_type="exchange",
                object_id=obj.pk,
            ).exists()
        return False


class InternshipSerializer(serializers.ModelSerializer):
    posted_by_info = UserPublicSerializer(source="posted_by", read_only=True)
    bookmarked = serializers.SerializerMethodField()
    posted_days = serializers.SerializerMethodField()
    apply_url = serializers.CharField(source="link", read_only=True)

    class Meta:
        model = Internship
        fields = [
            "id",
            "title",
            "company",
            "description",
            "location",
            "type",
            "duration",
            "deadline",
            "requirements",
            "salary_range",
            "link",
            "city",
            "country",
            "remote",
            "skills",
            "salary_min",
            "salary_max",
            "applicants_count",
            "apply_url",
            "bookmarked",
            "posted_days",
            "visibility",
            "is_published",
            "posted_by",
            "posted_by_info",
            "views_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "posted_by",
            "views_count",
            "applicants_count",
            "created_at",
            "updated_at",
        ]

    def get_bookmarked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            from apps.bookmarks.models import Bookmark

            return Bookmark.objects.filter(
                user=request.user,
                content_type="internship",
                object_id=obj.pk,
            ).exists()
        return False

    def get_posted_days(self, obj):
        from django.utils import timezone

        delta = timezone.now() - obj.created_at
        return delta.days


class StartupSerializer(serializers.ModelSerializer):
    posted_by_info = UserPublicSerializer(source="posted_by", read_only=True)
    posted_days = serializers.SerializerMethodField()

    class Meta:
        model = Startup
        fields = [
            "id",
            "title",
            "org_name",
            "description",
            "description_short",
            "city",
            "country",
            "tags",
            "equity_min",
            "equity_max",
            "contact_url",
            "followers_count",
            "posted_days",
            "visibility",
            "is_published",
            "posted_by",
            "posted_by_info",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["posted_by", "followers_count", "created_at", "updated_at"]

    def get_posted_days(self, obj):
        from django.utils import timezone

        delta = timezone.now() - obj.created_at
        return delta.days
