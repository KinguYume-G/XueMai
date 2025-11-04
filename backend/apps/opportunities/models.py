# Opportunities models
from django.db import models
from django.conf import settings


class ExchangeProgram(models.Model):
    """交换项目"""
    title = models.CharField(max_length=200, verbose_name="项目名称")
    description = models.TextField(verbose_name="项目描述")
    host_university = models.ForeignKey(
        "campus.University",
        on_delete=models.CASCADE,
        related_name="exchange_programs",
        verbose_name="主办大学"
    )
    location = models.CharField(max_length=200, verbose_name="地点")
    duration = models.CharField(max_length=100, blank=True, verbose_name="时长")
    deadline = models.DateField(null=True, blank=True, verbose_name="申请截止日期")
    requirements = models.TextField(blank=True, verbose_name="申请要求")
    link = models.URLField(blank=True, null=True, verbose_name="详情链接")
    
    visibility = models.CharField(
        max_length=20,
        choices=[
            ("public", "公开"),
            ("university", "同校可见"),
            ("private", "私密"),
        ],
        default="public",
        verbose_name="可见性"
    )
    is_published = models.BooleanField(default=True, verbose_name="已发布")
    
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posted_exchanges",
        verbose_name="发布者"
    )
    
    views_count = models.PositiveIntegerField(default=0, verbose_name="浏览数")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "交换项目"
        verbose_name_plural = "交换项目"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Internship(models.Model):
    """实习机会"""
    title = models.CharField(max_length=200, verbose_name="职位名称")
    company = models.CharField(max_length=200, verbose_name="公司名称")
    description = models.TextField(verbose_name="职位描述")
    location = models.CharField(max_length=200, verbose_name="地点")
    type = models.CharField(
        max_length=50,
        choices=[
            ("full_time", "全职"),
            ("part_time", "兼职"),
            ("internship", "实习"),
            ("remote", "远程"),
        ],
        verbose_name="类型"
    )
    duration = models.CharField(max_length=100, blank=True, verbose_name="时长")
    deadline = models.DateField(null=True, blank=True, verbose_name="申请截止日期")
    requirements = models.TextField(blank=True, verbose_name="职位要求")
    salary_range = models.CharField(max_length=100, blank=True, verbose_name="薪资范围")
    link = models.URLField(blank=True, null=True, verbose_name="申请链接")
    
    visibility = models.CharField(
        max_length=20,
        choices=[
            ("public", "公开"),
            ("university", "同校可见"),
            ("private", "私密"),
        ],
        default="public",
        verbose_name="可见性"
    )
    is_published = models.BooleanField(default=True, verbose_name="已发布")
    
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posted_internships",
        verbose_name="发布者"
    )
    
    views_count = models.PositiveIntegerField(default=0, verbose_name="浏览数")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "实习机会"
        verbose_name_plural = "实习机会"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} at {self.company}"

