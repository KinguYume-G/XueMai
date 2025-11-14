from rest_framework import serializers
from .models import Bookmark


class BookmarkSerializer(serializers.ModelSerializer):
    """收藏序列化器"""
    # 关联对象的详细信息（动态添加）
    item = serializers.SerializerMethodField()

    class Meta:
        model = Bookmark
        fields = ['id', 'content_type', 'object_id', 'created_at', 'item']

    def get_item(self, obj):
        """根据 content_type 返回对应的对象详情"""
        from apps.posts.models import Post
        from apps.opportunities.models import ExchangeProgram, Internship
        from apps.communities.models import Community
        from apps.posts.serializers import PostSerializer
        from apps.opportunities.serializers import ExchangeProgramSerializer, InternshipSerializer
        from apps.communities.serializers import CommunitySerializer

        if obj.content_type == 'post':
            try:
                post = Post.objects.get(id=obj.object_id)
                return PostSerializer(post, context=self.context).data
            except Post.DoesNotExist:
                return None

        elif obj.content_type == 'exchange':
            try:
                program = ExchangeProgram.objects.get(id=obj.object_id)
                return ExchangeProgramSerializer(program, context=self.context).data
            except ExchangeProgram.DoesNotExist:
                return None

        elif obj.content_type == 'internship':
            try:
                internship = Internship.objects.get(id=obj.object_id)
                return InternshipSerializer(internship, context=self.context).data
            except Internship.DoesNotExist:
                return None

        elif obj.content_type == 'community':
            try:
                community = Community.objects.get(id=obj.object_id)
                return CommunitySerializer(community, context=self.context).data
            except Community.DoesNotExist:
                return None

        return None
