# Social models
from django.db import models
from django.conf import settings


class Follow(models.Model):
    """关注关系"""
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following_set",
        verbose_name="关注者"
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followers_set",
        verbose_name="被关注者"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "关注关系"
        verbose_name_plural = "关注关系"
        unique_together = [["follower", "following"]]
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["follower", "-created_at"]),
            models.Index(fields=["following", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

    def save(self, *args, **kwargs):
        # 防止自己关注自己
        if self.follower == self.following:
            raise ValueError("用户不能关注自己")
        super().save(*args, **kwargs)


class Like(models.Model):
    """点赞（帖子或评论）"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="用户"
    )
    post = models.ForeignKey(
        'posts.Post',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="帖子"
    )
    comment = models.ForeignKey(
        'comments.Comment',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="评论"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "点赞"
        verbose_name_plural = "点赞"
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["post", "-created_at"]),
            models.Index(fields=["comment", "-created_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(post__isnull=False) | models.Q(comment__isnull=False),
                name='like_post_or_comment'
            ),
            models.UniqueConstraint(
                fields=['user', 'post'],
                condition=models.Q(post__isnull=False),
                name='unique_user_post_like'
            ),
            models.UniqueConstraint(
                fields=['user', 'comment'],
                condition=models.Q(comment__isnull=False),
                name='unique_user_comment_like'
            ),
        ]

    def __str__(self):
        if self.post:
            return f"{self.user.username} likes post {self.post.id}"
        return f"{self.user.username} likes comment {self.comment.id}"
