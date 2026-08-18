# Communities models
from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Community(models.Model):
    """社区模型"""

    CATEGORY_CHOICES = [
        ("interest", "兴趣爱好"),
        ("city", "城市"),
        ("oncampus", "校园"),
        ("study_group", "学习小组"),
    ]

    name = models.CharField(max_length=200, verbose_name="社区名称")
    slug = models.SlugField(max_length=220, unique=True, verbose_name="URL别名")
    description = models.TextField(blank=True, verbose_name="描述")
    cover_url = models.URLField(blank=True, null=True, verbose_name="封面图片URL")

    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default="interest", verbose_name="分类"
    )
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="城市")
    is_oncampus = models.BooleanField(default=False, verbose_name="是否校园社区")
    is_study_group = models.BooleanField(default=False, verbose_name="是否学习小组")

    # 统计字段
    members = models.PositiveIntegerField(default=0, verbose_name="成员数")
    activity_rate = models.FloatField(default=0.0, verbose_name="活跃度 0-1")

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

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_communities",
        verbose_name="创建者",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "社区"
        verbose_name_plural = "社区"
        ordering = ["-members", "-activity_rate"]
        indexes = [
            models.Index(fields=["category", "-members"]),
            models.Index(fields=["city"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class CommunityMember(models.Model):
    """社区成员关系"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="community_memberships",
        verbose_name="用户",
    )
    community = models.ForeignKey(
        Community, on_delete=models.CASCADE, related_name="memberships", verbose_name="社区"
    )
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="加入时间")

    class Meta:
        verbose_name = "社区成员"
        verbose_name_plural = "社区成员"
        unique_together = [["user", "community"]]
        ordering = ["-joined_at"]
        indexes = [
            models.Index(fields=["user", "community"]),
        ]

    def __str__(self):
        return f"{self.user.username} in {self.community.name}"
