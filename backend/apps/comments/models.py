# Comments models
from django.db import models
from django.conf import settings


class Comment(models.Model):
    """评论模型，支持楼中楼"""
    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="所属帖子"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="评论者"
    )
    content = models.TextField(verbose_name="评论内容")
    
    # 支持楼中楼（嵌套评论）
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        verbose_name="父评论"
    )
    
    likes_count = models.PositiveIntegerField(default=0, verbose_name="点赞数")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "评论"
        verbose_name_plural = "评论"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["post", "created_at"]),
            models.Index(fields=["parent"]),
        ]

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post}"

    @property
    def is_reply(self):
        """是否为回复评论"""
        return self.parent is not None
