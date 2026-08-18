# Forums models
from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Faculty(models.Model):
    """学院/专业分类"""

    name = models.CharField(max_length=200, unique=True, verbose_name="学院名称")
    slug = models.SlugField(max_length=220, unique=True, verbose_name="URL别名")
    icon_url = models.URLField(blank=True, null=True, verbose_name="图标URL")
    description = models.TextField(blank=True, verbose_name="描述")
    # 统计字段（第一版返回假数据，TODO: 实现真实统计）
    major_count = models.PositiveIntegerField(default=0, verbose_name="专业数量")
    topic_count = models.PositiveIntegerField(default=0, verbose_name="话题数量")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "学院"
        verbose_name_plural = "学院"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            import time

            from unidecode import unidecode

            # See Community.save() for why unidecode() runs first: plain
            # slugify() drops non-ASCII characters and can silently produce
            # an empty (and non-unique) slug for CJK-only names.
            base_slug = slugify(unidecode(self.name)) if self.name else ""
            if not base_slug:
                base_slug = f"faculty-{int(time.time())}"

            slug = base_slug
            counter = 2
            while Faculty.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Forum(models.Model):
    """论坛分类"""

    name = models.CharField(max_length=200, unique=True, verbose_name="名称")
    description = models.TextField(blank=True, verbose_name="描述")
    icon = models.CharField(max_length=50, blank=True, verbose_name="图标")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "论坛"
        verbose_name_plural = "论坛"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Topic(models.Model):
    visibility = models.CharField(
        max_length=20,
        choices=[
            ("public", "Public"),
            ("university", "University"),
            ("private", "Private"),
        ],
        default="public",
    )
    is_published = models.BooleanField(default=True)

    """论坛话题"""

    forum = models.ForeignKey(
        Forum, on_delete=models.CASCADE, related_name="topics", verbose_name="所属论坛"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="topics",
        verbose_name="作者",
    )
    title = models.CharField(max_length=200, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    tags = models.ManyToManyField("posts.Tag", blank=True, verbose_name="标签")

    views_count = models.PositiveIntegerField(default=0, verbose_name="浏览数")
    replies_count = models.PositiveIntegerField(default=0, verbose_name="回复数")

    is_pinned = models.BooleanField(default=False, verbose_name="置顶")
    is_solved = models.BooleanField(default=False, verbose_name="已解决")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "话题"
        verbose_name_plural = "话题"
        ordering = ["-is_pinned", "-updated_at"]
        indexes = [
            models.Index(fields=["-is_pinned", "-updated_at"]),
            models.Index(fields=["forum", "-created_at"]),
        ]

    def __str__(self):
        return self.title
