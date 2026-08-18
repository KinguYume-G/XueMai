# Posts serializers
from rest_framework import serializers

from apps.users.serializers import UserPublicSerializer

from .models import Bookmark, Post, PostLike, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug", "posts_count"]
        read_only_fields = ["slug", "posts_count"]


class PostSerializer(serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=50), write_only=True, required=False
    )
    is_liked = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "title",
            "body",
            "image_url",
            "visibility",
            "is_published",
            "target_university",
            "target_school",
            "tags",
            "tag_names",
            "likes_count",
            "comments_count",
            "bookmarks_count",
            "views_count",
            "is_liked",
            "is_bookmarked",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "author",
            "likes_count",
            "comments_count",
            "bookmarks_count",
            "views_count",
            "created_at",
            "updated_at",
        ]

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            # 使用prefetch的数据，避免N+1查询
            if hasattr(obj, "user_likes"):
                return bool(obj.user_likes)
            return PostLike.objects.filter(user=request.user, post=obj).exists()
        return False

    def get_is_bookmarked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            # 使用prefetch的数据，避免N+1查询
            if hasattr(obj, "user_bookmarks"):
                return bool(obj.user_bookmarks)
            return Bookmark.objects.filter(user=request.user, post=obj).exists()
        return False

    def create(self, validated_data):
        tag_names = validated_data.pop("tag_names", [])
        post = Post.objects.create(**validated_data)

        # 处理标签
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(name=tag_name.strip())
            post.tags.add(tag)
            tag.posts_count = tag.posts.count()
            tag.save()

        return post

    def update(self, instance, validated_data):
        tag_names = validated_data.pop("tag_names", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 更新标签
        if tag_names is not None:
            old_tags = list(instance.tags.all())
            instance.tags.clear()

            for old_tag in old_tags:
                old_tag.posts_count = old_tag.posts.count()
                old_tag.save()

            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name.strip())
                instance.tags.add(tag)
                tag.posts_count = tag.posts.count()
                tag.save()

        return instance


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=50), required=False, allow_empty=True
    )

    class Meta:
        model = Post
        fields = [
            "title",
            "body",
            "image_url",
            "visibility",
            "is_published",
            "target_university",
            "target_school",
            "tag_names",
        ]

    def validate_body(self, value):
        if len(value) > 5000:
            raise serializers.ValidationError("内容不能超过5000字符")
        return value

    def create(self, validated_data):
        tag_names = validated_data.pop("tag_names", [])
        post = Post.objects.create(**validated_data)

        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=tag_name.strip())
            post.tags.add(tag)
            tag.posts_count = tag.posts.count()
            tag.save()

        return post

    def update(self, instance, validated_data):
        tag_names = validated_data.pop("tag_names", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tag_names is not None:
            old_tags = list(instance.tags.all())
            instance.tags.clear()

            for old_tag in old_tags:
                old_tag.posts_count = old_tag.posts.count()
                old_tag.save()

            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=tag_name.strip())
                instance.tags.add(tag)
                tag.posts_count = tag.posts.count()
                tag.save()

        return instance
