# Notifications models
from django.db import models
from django.conf import settings


class Notification(models.Model):
    """通知模型"""

    TYPE_CHOICES = [
        ("like", "Like"),
        ("comment", "Comment"),
        ("follow", "Follow"),
        ("mention", "Mention"),
        ("system", "System"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="用户",
        null=True,
        blank=True,
    )
    type = models.CharField(
        max_length=16, choices=TYPE_CHOICES, default="system", verbose_name="类型"
    )
    title = models.CharField(max_length=200, default="通知", verbose_name="标题")
    content = models.TextField(blank=True, verbose_name="内容")
    link = models.CharField(max_length=500, blank=True, verbose_name="链接")
    is_read = models.BooleanField(default=False, verbose_name="已读")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "通知"
        verbose_name_plural = "通知"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["is_read"]),
        ]

    def __str__(self):
        return f"{self.type} for {self.user.username}"

    def mark_as_read(self):
        """标记为已读"""
        self.is_read = True
        self.save()
