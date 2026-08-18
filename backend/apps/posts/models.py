# Posts models
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from unidecode import unidecode  # type: ignore[import-not-found]


class Visibility(models.TextChoices):
    """可见性枚举"""

    PUBLIC = "public", "公开"
    FOLLOWERS = "followers", "仅关注者"
    UNIVERSITY = "university", "同校可见"
    PRIVATE = "private", "私密"


class Tag(models.Model):
    """标签模型"""

    name = models.CharField(max_length=50, unique=True, verbose_name="标签名")
    slug = models.SlugField(max_length=60, unique=True, blank=True, default="")
    posts_count = models.PositiveIntegerField(default=0, verbose_name="帖子数")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "标签"
        verbose_name_plural = "标签"
        ordering = ["-posts_count", "name"]
        db_table = "posts_tag"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not (self.slug and self.slug.strip()):
            base = slugify(unidecode((self.name or "").strip())) or "tag"
            candidate = base
            i = 2
            while Tag.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base}-{i}"
                i += 1
            self.slug = candidate
        super().save(*args, **kwargs)


class PostQuerySet(models.QuerySet):
    """帖子查询集，实现可见性过滤"""

    def visible_to(self, user):
        """过滤当前用户可见的帖子"""
        if not user or not user.is_authenticated:
            # 未登录用户只能看公开帖子
            return self.filter(visibility=Visibility.PUBLIC, is_published=True)

        # 已登录用户：自己的帖子 + 公开帖子 + 关注者帖子（如果关注了作者） + 同校帖子
        from apps.social.models import Follow

        # 获取用户关注的人的ID列表
        following_ids = Follow.objects.filter(follower=user).values_list("following_id", flat=True)

        # 获取用户的大学ID
        user_university_id = None
        if hasattr(user, "profile") and user.profile.university_id:
            user_university_id = user.profile.university_id

        q = models.Q(author=user)  # 自己的帖子
        q |= models.Q(visibility=Visibility.PUBLIC, is_published=True)  # 公开帖子
        q |= models.Q(
            visibility=Visibility.FOLLOWERS,
            author_id__in=following_ids,
            is_published=True,
        )  # 关注者帖子

        if user_university_id:
            q |= models.Q(
                visibility=Visibility.UNIVERSITY,
                target_university_id=user_university_id,
                is_published=True,
            )

        return self.filter(q)


class Post(models.Model):
    """帖子模型"""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="作者",
    )
    title = models.CharField(max_length=200, blank=True, verbose_name="标题")
    body = models.TextField(verbose_name="内容")
    image_url = models.URLField(blank=True, null=True, verbose_name="图片链接")

    visibility = models.CharField(
        max_length=20,
        choices=Visibility.choices,
        default=Visibility.PUBLIC,
        verbose_name="可见性",
    )
    is_published = models.BooleanField(default=True, verbose_name="已发布")

    # 目标受众（用于同校可见）
    target_university = models.ForeignKey(
        "campus.University",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="targeted_posts",
        verbose_name="目标大学",
    )
    target_school = models.ForeignKey(
        "campus.School",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="targeted_posts",
        verbose_name="目标学院",
    )

    tags = models.ManyToManyField(Tag, blank=True, related_name="posts", verbose_name="标签")

    # 统计字段
    likes_count = models.PositiveIntegerField(default=0, verbose_name="点赞数")
    comments_count = models.PositiveIntegerField(default=0, verbose_name="评论数")
    bookmarks_count = models.PositiveIntegerField(default=0, verbose_name="收藏数")
    views_count = models.PositiveIntegerField(default=0, verbose_name="浏览数")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PostQuerySet.as_manager()

    class Meta:
        verbose_name = "帖子"
        verbose_name_plural = "帖子"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["visibility", "is_published"]),
        ]

    def __str__(self):
        return self.title or f"Post by {self.author.username}"


class PostLike(models.Model):
    """帖子点赞"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="post_likes",
        verbose_name="用户",
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="post_likes", verbose_name="帖子"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "帖子点赞"
        verbose_name_plural = "帖子点赞"
        unique_together = [["user", "post"]]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} likes {self.post}"


class Bookmark(models.Model):
    """收藏"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookmarks",
        verbose_name="用户",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="bookmarked_by",
        verbose_name="帖子",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "收藏"
        verbose_name_plural = "收藏"
        unique_together = [["user", "post"]]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} bookmarked {self.post}"
