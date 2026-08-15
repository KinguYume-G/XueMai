# Forums serializers
from rest_framework import serializers
from .models import Forum, Topic, Faculty
from apps.users.serializers import UserSerializer
from apps.posts.serializers import TagSerializer
from django.db.models import Count


class FacultySerializer(serializers.ModelSerializer):
    """学院序列化器"""
    hot_tags = serializers.SerializerMethodField()

    class Meta:
        model = Faculty
        fields = [
            'id', 'name', 'slug', 'icon_url', 'description',
            'major_count', 'topic_count', 'hot_tags', 'created_at'
        ]
        read_only_fields = ['created_at']

    def get_hot_tags(self, obj):
        return list(
            Topic.objects.filter(forum__name__icontains=obj.name)
            .exclude(tags__name__isnull=True)
            .values('tags__name')
            .annotate(total=Count('id'))
            .order_by('-total', 'tags__name')
            .values_list('tags__name', flat=True)[:3]
        )


class ForumSerializer(serializers.ModelSerializer):
    topics_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Forum
        fields = ['id', 'name', 'description', 'icon', 'topics_count', 'created_at']
        read_only_fields = ['created_at']
    
    def get_topics_count(self, obj):
        return obj.topics.count()


class TopicSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    forum_name = serializers.CharField(source='forum.name', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Topic
        fields = [
            'id', 'forum', 'forum_name', 'author', 'title', 'content',
            'tags', 'tag_names', 'views_count', 'replies_count',
            'is_pinned', 'is_solved', 'created_at', 'updated_at'
        ]
        read_only_fields = ['author', 'views_count', 'replies_count', 
                           'created_at', 'updated_at']
    
    def create(self, validated_data):
        tag_names = validated_data.pop('tag_names', [])
        topic = Topic.objects.create(**validated_data)
        
        # 处理标签
        from apps.posts.models import Tag
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(name=tag_name.strip())
            topic.tags.add(tag)
        
        return topic


class TopicCreateSerializer(serializers.ModelSerializer):
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = Topic
        fields = ['forum', 'title', 'content', 'tag_names']
