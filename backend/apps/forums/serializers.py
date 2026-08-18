# Forums serializers
from rest_framework import serializers

from apps.posts.serializers import TagSerializer
from apps.users.serializers import UserPublicSerializer

from .models import Faculty, Forum, Topic


class FacultySerializer(serializers.ModelSerializer):
    """学院序列化器"""

    hot_tags = serializers.SerializerMethodField()

    class Meta:
        model = Faculty
        fields = [
            "id",
            "name",
            "slug",
            "icon_url",
            "description",
            "major_count",
            "topic_count",
            "hot_tags",
            "created_at",
        ]
        read_only_fields = ["created_at"]

    def get_hot_tags(self, obj):
        # TODO: 实现真实的热门标签统计逻辑
        # 第一版返回假数据
        hot_tags_map = {
            "computing": ["软件工程", "人工智能", "网络安全"],
            "business": ["市场营销", "创业", "金融"],
            "engineering": ["机械设计", "电子工程", "材料科学"],
        }
        return hot_tags_map.get(obj.slug, ["课程资料", "学术讨论", "经验分享"])


class ForumSerializer(serializers.ModelSerializer):
    topics_count = serializers.SerializerMethodField()

    class Meta:
        model = Forum
        fields = ["id", "name", "description", "icon", "topics_count", "created_at"]
        read_only_fields = ["created_at"]

    def get_topics_count(self, obj):
        return obj.topics.count()


class TopicSerializer(serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)
    forum_name = serializers.CharField(source="forum.name", read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=50), write_only=True, required=False
    )

    class Meta:
        model = Topic
        fields = [
            "id",
            "forum",
            "forum_name",
            "author",
            "title",
            "content",
            "tags",
            "tag_names",
            "views_count",
            "replies_count",
            "is_pinned",
            "is_solved",
            "visibility",
            "is_published",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["author", "views_count", "replies_count", "created_at", "updated_at"]

    def create(self, validated_data):
        tag_names = validated_data.pop("tag_names", [])
        topic = Topic.objects.create(**validated_data)

        # 处理标签
        from apps.posts.models import Tag

        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(name=tag_name.strip())
            topic.tags.add(tag)

        return topic

    def update(self, instance, validated_data):
        # get_serializer_class() only swaps in TopicCreateSerializer for the
        # "create" action, so this is the serializer PATCH/PUT actually use.
        # Without this override, ModelSerializer's default update() would
        # setattr() tag_names onto the instance (a no-op, since it isn't a
        # real model field) and silently drop the caller's tag changes.
        tag_names = validated_data.pop("tag_names", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tag_names is not None:
            from apps.posts.models import Tag

            instance.tags.clear()
            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=tag_name.strip())
                instance.tags.add(tag)

        return instance


class TopicCreateSerializer(serializers.ModelSerializer):
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=50), required=False, allow_empty=True
    )

    class Meta:
        model = Topic
        fields = [
            "forum",
            "title",
            "content",
            "tag_names",
            "visibility",
            "is_published",
        ]

    def create(self, validated_data):
        tag_names = validated_data.pop("tag_names", [])
        topic = Topic.objects.create(**validated_data)

        from apps.posts.models import Tag

        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=tag_name.strip())
            topic.tags.add(tag)

        return topic
