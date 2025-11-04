# Forums models
from django.db import models
from django.conf import settings


class Forum(models.Model):
    """论坛分类"""
    name = models.CharField(max_length=200, unique=True, verbose_name="名称")
    description = models.TextField(blank=True, verbose_name="描述")
    icon = models.CharField(max_length=50, blank=True, verbose_name="图标")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "论坛"
        verbose_name_plural = "论坛"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Topic(models.Model):
    """论坛话题"""
    forum = models.ForeignKey(
        Forum,
        on_delete=models.CASCADE,
        related_name="topics",
        verbose_name="所属论坛"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="topics",
        verbose_name="作者"
    )
    title = models.CharField(max_length=200, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    tags = models.ManyToManyField('posts.Tag', blank=True, verbose_name="标签")
    
    views_count = models.PositiveIntegerField(default=0, verbose_name="浏览数")
    replies_count = models.PositiveIntegerField(default=0, verbose_name="回复数")
    
    is_pinned = models.BooleanField(default=False, verbose_name="置顶")
    is_solved = models.BooleanField(default=False, verbose_name="已解决")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "话题"
        verbose_name_plural = "话题"
        ordering = ['-is_pinned', '-updated_at']
        indexes = [
            models.Index(fields=['-is_pinned', '-updated_at']),
            models.Index(fields=['forum', '-created_at']),
        ]
    
    def __str__(self):
        return self.title

