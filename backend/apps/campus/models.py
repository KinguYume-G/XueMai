from django.db import models
from django.utils.text import slugify
from django.conf import settings


class University(models.Model):
    """大学模型"""
    name = models.CharField(max_length=200, unique=True, verbose_name="大学名称")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    country = models.CharField(max_length=100, verbose_name="国家")
    city = models.CharField(max_length=100, verbose_name="城市")
    logo = models.URLField(blank=True, null=True, verbose_name="Logo URL")
    website = models.URLField(blank=True, null=True, verbose_name="官网")
    description = models.TextField(blank=True, verbose_name="简介")
    students_count = models.PositiveIntegerField(default=0, verbose_name="学生数")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "大学"
        verbose_name_plural = "大学"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from unidecode import unidecode
            import time

            base_slug = slugify(unidecode(self.name)) if self.name else ""
            if not base_slug:
                base_slug = f"university-{int(time.time())}"

            # Ensure uniqueness across all universities; start suffix from 2 per spec
            slug = base_slug
            counter = 2
            while University.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug
        super().save(*args, **kwargs)


class School(models.Model):
    """学院/系模型"""
    university = models.ForeignKey(
        University, 
        on_delete=models.CASCADE, 
        related_name="schools",
        verbose_name="所属大学"
    )
    name = models.CharField(max_length=200, verbose_name="学院名称")
    slug = models.SlugField(max_length=200, blank=True)
    description = models.TextField(blank=True, verbose_name="简介")
    students_count = models.PositiveIntegerField(default=0, verbose_name="学生数")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "学院"
        verbose_name_plural = "学院"
        ordering = ["university", "name"]
        unique_together = [["university", "name"]]

    def __str__(self):
        return f"{self.university.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            from unidecode import unidecode
            import time

            base_slug = slugify(unidecode(self.name)) if self.name else ""
            if not base_slug:
                base_slug = f"school-{int(time.time())}"

            # Ensure uniqueness within the same university
            slug = base_slug
            counter = 2
            qs = School.objects.filter(university=self.university)
            while qs.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug
        super().save(*args, **kwargs)


class UniversityResource(models.Model):
    """大学资源模型（课程、食堂、社团、活动等）"""
    
    CATEGORY_CHOICES = [
        ('course', '课程'),
        ('canteen', '食堂'),
        ('club', '社团'),
        ('event', '活动'),
        ('notice', '通知'),
    ]
    
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name='resources',
        verbose_name="所属大学"
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name="类别"
    )
    title = models.CharField(max_length=200, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    extra = models.JSONField(
        blank=True,
        null=True,
        default=dict,
        verbose_name="额外信息"
    )
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_resources',
        verbose_name="创建者"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "大学资源"
        verbose_name_plural = "大学资源"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['university', 'category']),
            models.Index(fields=['is_active', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.university.name} - {self.get_category_display()} - {self.title}"

