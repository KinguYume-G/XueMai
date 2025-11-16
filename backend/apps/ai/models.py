from django.db import models
from django.conf import settings


class AIDocument(models.Model):
    """AI文档模型 - 存储原始文档"""
    
    DOC_TYPE_CHOICES = [
        ('course', '课程资料'),
        ('regulation', '校规'),
        ('announcement', '公告'),
        ('post', '帖子'),
        ('other', '其他'),
    ]
    
    university = models.ForeignKey(
        'campus.University',
        on_delete=models.CASCADE,
        related_name='ai_documents',
        verbose_name="所属大学",
        null=True,
        blank=True
    )
    doc_type = models.CharField(
        max_length=20,
        choices=DOC_TYPE_CHOICES,
        verbose_name="文档类型"
    )
    title = models.CharField(max_length=500, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    source_url = models.URLField(blank=True, null=True, verbose_name="来源URL")
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="元数据"
    )
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_ai_documents',
        verbose_name="上传者"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "AI文档"
        verbose_name_plural = "AI文档"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['university', 'doc_type']),
            models.Index(fields=['is_active', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_doc_type_display()} - {self.title}"


class AIChunk(models.Model):
    """AI文本块模型 - 文档分块后的片段"""
    
    document = models.ForeignKey(
        AIDocument,
        on_delete=models.CASCADE,
        related_name='chunks',
        verbose_name="所属文档"
    )
    content = models.TextField(verbose_name="块内容")
    chunk_index = models.IntegerField(verbose_name="块序号")
    chunk_metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="块元数据"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "AI文本块"
        verbose_name_plural = "AI文本块"
        ordering = ['document', 'chunk_index']
        unique_together = [['document', 'chunk_index']]
        indexes = [
            models.Index(fields=['document', 'chunk_index']),
        ]
    
    def __str__(self):
        return f"{self.document.title} - Chunk {self.chunk_index}"


class AIEmbedding(models.Model):
    """AI向量嵌入模型 - 存储向量"""
    
    chunk = models.OneToOneField(
        AIChunk,
        on_delete=models.CASCADE,
        related_name='embedding',
        verbose_name="所属文本块"
    )
    # 使用 pgvector 扩展的 vector 字段
    # 注意：需要安装 pgvector 扩展
    # embedding = VectorField(dimensions=1536)  # OpenAI embeddings 维度
    # 临时使用 JSONField 存储，等 pgvector 配置好后再改
    embedding_vector = models.JSONField(
        verbose_name="向量数据",
        help_text="临时使用JSON存储，后续迁移到pgvector"
    )
    embedding_model = models.CharField(
        max_length=100,
        default='text-embedding-ada-002',
        verbose_name="嵌入模型"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "AI向量嵌入"
        verbose_name_plural = "AI向量嵌入"
        indexes = [
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Embedding for {self.chunk}"


class AIQueryLog(models.Model):
    """AI查询日志模型 - 记录用户查询历史"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_queries',
        verbose_name="查询用户"
    )
    query_text = models.TextField(verbose_name="查询文本")
    response_text = models.TextField(verbose_name="响应文本")
    university = models.ForeignKey(
        'campus.University',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_queries',
        verbose_name="关联大学"
    )
    matched_chunks = models.JSONField(
        default=list,
        blank=True,
        verbose_name="匹配的文本块ID列表"
    )
    response_time_ms = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="响应时间(毫秒)"
    )
    is_helpful = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="是否有帮助"
    )
    feedback_text = models.TextField(
        blank=True,
        verbose_name="用户反馈"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="查询时间")
    
    class Meta:
        verbose_name = "AI查询日志"
        verbose_name_plural = "AI查询日志"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['university', '-created_at']),
            models.Index(fields=['-created_at']),  # 按时间排序查询
            models.Index(fields=['user', 'university', '-created_at']),  # 复合查询
            models.Index(fields=['response_time_ms']),  # 性能分析
            models.Index(fields=['is_helpful', '-created_at']),  # 质量监控
        ]
    
    def __str__(self):
        user_str = self.user.username if self.user else "Anonymous"
        return f"{user_str} - {self.query_text[:50]}"

