# Notifications models
from django.conf import settings
from django.db import models
from django.utils import timezone


class Notification(models.Model):
    """通知模型"""

    TYPE_CHOICES = [
        ("like", "Like"),
        ("comment", "Comment"),
        ("follow", "Follow"),
        ("mention", "Mention"),
        ("system", "System"),
    ]

    # 接收者 (原 user 字段)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="接收者",
        null=True,
        blank=True,
    )

    # 发送者 (触发通知的用户，系统通知可为 NULL)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_notifications",
        verbose_name="发送者",
        null=True,
        blank=True,
    )

    type = models.CharField(
        max_length=16, choices=TYPE_CHOICES, default="system", verbose_name="类型"
    )
    title = models.CharField(max_length=200, default="通知", verbose_name="标题")
    content = models.TextField(blank=True, verbose_name="内容")
    link = models.CharField(max_length=500, blank=True, verbose_name="链接")

    # 关联的帖子
    related_post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="关联帖子",
        null=True,
        blank=True,
    )

    # 关联的评论
    related_comment = models.ForeignKey(
        "comments.Comment",
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="关联评论",
        null=True,
        blank=True,
    )

    is_read = models.BooleanField(default=False, verbose_name="已读")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="阅读时间")

    class Meta:
        verbose_name = "通知"
        verbose_name_plural = "通知"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["user", "type"]),
        ]

    def __str__(self):
        username = self.user.username if self.user else "Unknown"
        return f"{self.type} for {username}"

    def mark_as_read(self):
        """标记为已读"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])
