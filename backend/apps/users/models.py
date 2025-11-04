# User models
# apps/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """自定义用户模型"""

    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    bio = models.TextField(blank=True, default="", verbose_name="个人简介")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return self.username


class Profile(models.Model):
    """用户扩展资料"""

    GRADE_CHOICES = [
        ("freshman", "大一"),
        ("sophomore", "大二"),
        ("junior", "大三"),
        ("senior", "大四"),
        ("master", "硕士"),
        ("phd", "博士"),
        ("alumni", "校友"),
        ("other", "其他"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    university = models.ForeignKey(
        "campus.University",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profiles",
        verbose_name="所属大学",
    )
    school = models.ForeignKey(
        "campus.School",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profiles",
        verbose_name="所属学院",
    )
    avatar_url = models.URLField(blank=True, verbose_name="头像URL")
    major = models.CharField(max_length=100, blank=True, verbose_name="专业")
    grade = models.CharField(
        max_length=20, choices=GRADE_CHOICES, blank=True, verbose_name="年级"
    )

    # 社交统计
    followers_count = models.PositiveIntegerField(default=0, verbose_name="粉丝数")
    following_count = models.PositiveIntegerField(default=0, verbose_name="关注数")
    posts_count = models.PositiveIntegerField(default=0, verbose_name="帖子数")

    # 社交链接
    github_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, default="", verbose_name="个人简介")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "用户资料"
        verbose_name_plural = "用户资料"

    def __str__(self):
        return f"{self.user.username} - Profile"
