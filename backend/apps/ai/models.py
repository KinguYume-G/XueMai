from django.conf import settings
from django.db import models
from pgvector.django import VectorField


class AIDocument(models.Model):
    """AI文档模型 - 存储原始文档"""

    DOC_TYPE_CHOICES = [
        ("course", "课程资料"),
        ("regulation", "校规"),
        ("announcement", "公告"),
        ("post", "帖子"),
        ("resume", "简历模板"),
        ("business_plan", "BP模板"),
        ("company", "公司信息"),
        ("market_report", "市场报告"),
        ("salary", "薪资数据"),
        ("other", "其他"),
    ]

    university = models.ForeignKey(
        "campus.University",
        on_delete=models.CASCADE,
        related_name="ai_documents",
        verbose_name="所属大学",
        null=True,
        blank=True,
    )
    doc_type = models.CharField(
        max_length=20,
        choices=DOC_TYPE_CHOICES,
        verbose_name="文档类型",
    )
    title = models.CharField(max_length=500, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    source_url = models.URLField(blank=True, null=True, verbose_name="来源URL")
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="元数据",
    )
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_ai_documents",
        verbose_name="上传者",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "AI文档"
        verbose_name_plural = "AI文档"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["university", "doc_type"]),
            models.Index(fields=["is_active", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.get_doc_type_display()} - {self.title}"


class AIChunk(models.Model):
    """AI文本块模型 - 文档分块后的片段"""

    document = models.ForeignKey(
        AIDocument,
        on_delete=models.CASCADE,
        related_name="chunks",
        verbose_name="所属文档",
    )
    content = models.TextField(verbose_name="块内容")
    chunk_index = models.IntegerField(verbose_name="块序号")
    chunk_metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="块元数据",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "AI文本块"
        verbose_name_plural = "AI文本块"
        ordering = ["document", "chunk_index"]
        unique_together = [["document", "chunk_index"]]
        indexes = [
            models.Index(fields=["document", "chunk_index"]),
        ]

    def __str__(self):
        return f"{self.document.title} - Chunk {self.chunk_index}"


class AIEmbedding(models.Model):
    """AI向量嵌入模型 - 存储向量"""

    chunk = models.OneToOneField(
        AIChunk,
        on_delete=models.CASCADE,
        related_name="embedding",
        verbose_name="所属文本块",
    )

    # ✅ 使用 pgvector 的向量字段，维度改为 768，和 Ollama 的 nomic-embed-text 对齐
    embedding_vector = VectorField(
        dimensions=768,
        verbose_name="向量数据",
        help_text="使用 pgvector 存储的向量",
        null=True,
        blank=True,  # 迁移阶段允许为空
    )

    # ✅ 默认模型名称改为当前实际使用的 embedding 模型
    embedding_model = models.CharField(
        max_length=100,
        default="nomic-embed-text",
        verbose_name="嵌入模型",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "AI向量嵌入"
        verbose_name_plural = "AI向量嵌入"
        indexes = [
            models.Index(fields=["created_at"]),
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
        related_name="ai_queries",
        verbose_name="查询用户",
    )
    query_text = models.TextField(verbose_name="查询文本")
    response_text = models.TextField(verbose_name="响应文本")
    university = models.ForeignKey(
        "campus.University",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_queries",
        verbose_name="关联大学",
    )
    matched_chunks = models.JSONField(
        default=list,
        blank=True,
        verbose_name="匹配的文本块ID列表",
    )
    response_time_ms = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="响应时间(毫秒)",
    )
    is_helpful = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="是否有帮助",
    )
    feedback_text = models.TextField(
        blank=True,
        verbose_name="用户反馈",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="查询时间")

    class Meta:
        verbose_name = "AI查询日志"
        verbose_name_plural = "AI查询日志"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["university", "-created_at"]),
            models.Index(fields=["-created_at"]),
            models.Index(fields=["user", "university", "-created_at"]),
            models.Index(fields=["response_time_ms"]),
            models.Index(fields=["is_helpful", "-created_at"]),
        ]

    def __str__(self):
        user_str = self.user.username if self.user else "Anonymous"
        return f"{user_str} - {self.query_text[:50]}"


class AIConversation(models.Model):
    """AI 对话会话模型 - 记录对话会话元信息"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_conversations",
        verbose_name="用户",
    )
    title = models.CharField(
        max_length=200,
        default="新对话",
        verbose_name="会话标题",
    )
    ai_function = models.CharField(
        max_length=50,
        verbose_name="AI功能",
        help_text="例如：智能对话、简历优化等",
    )
    
    # 上下文管理字段
    context_summary = models.TextField(
        blank=True,
        verbose_name="上下文摘要",
        help_text="会话上下文的压缩摘要",
    )
    total_tokens = models.IntegerField(
        default=0,
        verbose_name="累计Token数",
        help_text="当前会话使用的总token数",
    )
    context_metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="上下文元数据",
        help_text="用户画像、偏好等信息",
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "AI对话"
        verbose_name_plural = "AI对话"
        db_table = "ai_conversations"
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["user", "-updated_at"]),
            models.Index(fields=["-updated_at"]),
        ]

    def get_message_count(self) -> int:
        """返回会话下的消息数量"""
        return self.messages.count()

    def __str__(self):
        return f"{self.user_id} - {self.title}"


class AIMessage(models.Model):
    """AI 对话消息模型 - 记录单条对话消息"""

    ROLE_CHOICES = [
        ("user", "用户"),
        ("assistant", "AI助手"),
        ("system", "系统"),
    ]

    conversation = models.ForeignKey(
        AIConversation,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="所属会话",
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        verbose_name="角色",
    )
    content = models.TextField(verbose_name="消息内容")
    tokens = models.IntegerField(
        default=0,
        verbose_name="Token数量",
        help_text="可选字段，用于记录该消息的大致 token 数",
    )
    model_used = models.CharField(
        max_length=50,
        verbose_name="使用模型",
        help_text="记录本条消息使用的模型名称",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "AI消息"
        verbose_name_plural = "AI消息"
        db_table = "ai_messages"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["conversation", "created_at"]),
            models.Index(fields=["role", "created_at"]),
        ]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"


class AIRoutingLog(models.Model):
    """AI路由日志 - 记录意图识别决策（用于后续优化）"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="routing_logs",
        verbose_name="用户",
    )
    query = models.TextField(verbose_name="用户查询")
    recognized_function = models.CharField(
        max_length=50,
        verbose_name="识别的功能",
    )
    confidence = models.FloatField(
        verbose_name="置信度",
        help_text="识别置信度 0.0-1.0",
    )
    method = models.CharField(
        max_length=20,
        verbose_name="识别方法",
        help_text="mode, keyword, semantic, llm, default",
    )
    reasoning = models.TextField(
        blank=True,
        verbose_name="推理过程",
        help_text="为什么选择这个功能",
    )
    manual_mode = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="手动指定模式",
        help_text="如果用户手动指定mode，记录在此",
    )
    is_correct = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="是否正确",
        help_text="后续人工标注或用户反馈",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "AI路由日志"
        verbose_name_plural = "AI路由日志"
        db_table = "ai_routing_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["recognized_function", "-created_at"]),
            models.Index(fields=["method", "-created_at"]),
            models.Index(fields=["confidence"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.recognized_function} ({self.confidence:.2f}) - {self.query[:30]}"
