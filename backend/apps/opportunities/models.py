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

    # 新增字段
    cover_url = models.URLField(blank=True, null=True, verbose_name="封面图片URL")
    tuition = models.CharField(max_length=100, blank=True, null=True, verbose_name="学费")
    stipend = models.CharField(max_length=100, blank=True, null=True, verbose_name="奖学金")
    gpa_min = models.CharField(max_length=20, blank=True, null=True, verbose_name="最低GPA要求")
    lang_req = models.CharField(max_length=200, blank=True, null=True, verbose_name="语言要求")
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name="国家")

    # 统计字段（第一版可返回固定值）
    rating_avg = models.FloatField(default=0.0, verbose_name="平均评分")
    rating_count = models.PositiveIntegerField(default=0, verbose_name="评分数量")
    applied_count = models.PositiveIntegerField(default=0, verbose_name="申请人数")

    # 额外字段
    website = models.URLField(blank=True, null=True, verbose_name="官网链接")
    is_urgent = models.BooleanField(default=False, verbose_name="是否即将截止")

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

    # 新增字段
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="城市")
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name="国家")
    remote = models.BooleanField(default=False, verbose_name="是否远程")
    skills = models.JSONField(default=list, blank=True, verbose_name="所需技能")
    salary_min = models.PositiveIntegerField(null=True, blank=True, verbose_name="最低薪资")
    salary_max = models.PositiveIntegerField(null=True, blank=True, verbose_name="最高薪资")
    applicants_count = models.PositiveIntegerField(default=0, verbose_name="申请人数")

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


class Startup(models.Model):
    """创业机会"""
    title = models.CharField(max_length=200, verbose_name="项目名称")
    org_name = models.CharField(max_length=200, verbose_name="组织名称")
    description = models.TextField(verbose_name="项目描述")
    description_short = models.CharField(max_length=500, blank=True, verbose_name="简短描述")
    city = models.CharField(max_length=100, verbose_name="城市")
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name="国家")

    tags = models.JSONField(default=list, blank=True, verbose_name="标签")
    equity_min = models.FloatField(null=True, blank=True, verbose_name="最低股权比例%")
    equity_max = models.FloatField(null=True, blank=True, verbose_name="最高股权比例%")

    contact_url = models.URLField(blank=True, null=True, verbose_name="联系方式URL")
    followers_count = models.PositiveIntegerField(default=0, verbose_name="关注人数")

    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posted_startups",
        verbose_name="发布者"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "创业机会"
        verbose_name_plural = "创业机会"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.org_name}"

