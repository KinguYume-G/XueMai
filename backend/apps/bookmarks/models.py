from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Bookmark(models.Model):
    """收藏模型 - 支持多种内容类型"""

    CONTENT_TYPE_CHOICES = [
        ('post', '帖子'),
        ('exchange', '交换项目'),
        ('internship', '实习机会'),
        ('community', '社区'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_bookmarks',
        verbose_name="用户"
    )
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPE_CHOICES,
        verbose_name="内容类型"
    )
    object_id = models.IntegerField(verbose_name="对象ID")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="收藏时间")

    class Meta:
        db_table = 'bookmarks'
        unique_together = [['user', 'content_type', 'object_id']]  # 同一用户不能重复收藏
        ordering = ['-created_at']
        verbose_name = "收藏"
        verbose_name_plural = "收藏"

    def __str__(self):
        return f"{self.user.username} - {self.content_type} - {self.object_id}"
