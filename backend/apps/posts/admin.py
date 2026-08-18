# Posts admin
from django.contrib import admin

from .models import Bookmark, Post, PostLike, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "posts_count", "created_at"]
    search_fields = ["name"]
    readonly_fields = ["slug", "posts_count", "created_at"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "author",
        "visibility",
        "is_published",
        "likes_count",
        "comments_count",
        "created_at",
    ]
    list_filter = ["visibility", "is_published", "created_at"]
    search_fields = ["title", "body"]
    raw_id_fields = ["author", "target_university", "target_school"]
    filter_horizontal = ["tags"]
    readonly_fields = [
        "likes_count",
        "comments_count",
        "bookmarks_count",
        "views_count",
        "created_at",
        "updated_at",
    ]


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ["user", "post", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__username", "post__title"]
    raw_id_fields = ["user", "post"]


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ["user", "post", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__username", "post__title"]
    raw_id_fields = ["user", "post"]
