# Social models
from django.conf import settings
from django.db import models


class Follow(models.Model):
    """关注关系"""

    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following_set",
        verbose_name="关注者",
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followers_set",
        verbose_name="被关注者",
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
        verbose_name="用户",
    )
    post = models.ForeignKey(
        "posts.Post",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="帖子",
    )
    comment = models.ForeignKey(
        "comments.Comment",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="评论",
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
                condition=models.Q(post__isnull=False) | models.Q(comment__isnull=False),
                name="like_post_or_comment",
            ),
            models.UniqueConstraint(
                fields=["user", "post"],
                condition=models.Q(post__isnull=False),
                name="unique_user_post_like",
            ),
            models.UniqueConstraint(
                fields=["user", "comment"],
                condition=models.Q(comment__isnull=False),
                name="unique_user_comment_like",
            ),
        ]

    def __str__(self):
        if self.post:
            return f"{self.user.username} likes post {self.post.id}"
        return f"{self.user.username} likes comment {self.comment.id}"


class FriendRequest(models.Model):
    """好友申请"""

    STATUS_CHOICES = [
        ("pending", "待处理"),
        ("accepted", "已接受"),
        ("rejected", "已拒绝"),
    ]

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_friend_requests",
        verbose_name="发送者",
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_friend_requests",
        verbose_name="接收者",
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="状态"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="申请时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "好友申请"
        verbose_name_plural = "好友申请"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["to_user", "status", "-created_at"]),
            models.Index(fields=["from_user", "status", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username} ({self.status})"

    def accept(self):
        """接受好友申请，创建双向关注关系"""
        self.status = "accepted"
        self.save()

        # 创建双向关注关系
        Follow.objects.get_or_create(follower=self.from_user, following=self.to_user)
        Follow.objects.get_or_create(follower=self.to_user, following=self.from_user)

    def reject(self):
        """拒绝好友申请"""
        self.status = "rejected"
        self.save()


class ChatGroup(models.Model):
    """群组"""

    name = models.CharField(max_length=200, verbose_name="群组名称")
    description = models.TextField(blank=True, verbose_name="群组描述")
    avatar_url = models.URLField(blank=True, null=True, verbose_name="群组头像")
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_groups",
        verbose_name="创建者",
    )
    member_count = models.IntegerField(default=0, verbose_name="成员数量")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "群组"
        verbose_name_plural = "群组"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["creator"]),
        ]

    def __str__(self):
        return self.name

    def update_member_count(self):
        """更新成员数量"""
        self.member_count = self.members.count()
        self.save(update_fields=["member_count"])

    def add_member(self, user, role="member"):
        """添加成员"""
        member, created = GroupMember.objects.get_or_create(
            group=self, user=user, defaults={"role": role}
        )
        if created:
            self.update_member_count()
        return member

    def remove_member(self, user):
        """移除成员"""
        deleted_count, _ = GroupMember.objects.filter(group=self, user=user).delete()
        if deleted_count > 0:
            self.update_member_count()


class GroupMember(models.Model):
    """群组成员"""

    ROLE_CHOICES = [
        ("owner", "群主"),
        ("admin", "管理员"),
        ("member", "普通成员"),
    ]

    group = models.ForeignKey(
        ChatGroup, on_delete=models.CASCADE, related_name="members", verbose_name="群组"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="group_memberships",
        verbose_name="用户",
    )
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default="member", verbose_name="角色"
    )
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="加入时间")

    class Meta:
        verbose_name = "群组成员"
        verbose_name_plural = "群组成员"
        unique_together = [["group", "user"]]
        ordering = ["group", "-joined_at"]
        indexes = [
            models.Index(fields=["user", "-joined_at"]),
            models.Index(fields=["group", "-joined_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} in {self.group.name} ({self.role})"


class ChatMessage(models.Model):
    """聊天消息"""

    MESSAGE_TYPE_CHOICES = [
        ("text", "文本"),
        ("image", "图片"),
        ("file", "文件"),
        ("emoji", "表情"),
    ]

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        verbose_name="发送者",
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_messages",
        null=True,
        blank=True,
        verbose_name="接收者",
    )
    group = models.ForeignKey(
        ChatGroup,
        on_delete=models.CASCADE,
        related_name="messages",
        null=True,
        blank=True,
        verbose_name="群组",
    )
    content = models.TextField(verbose_name="消息内容")
    message_type = models.CharField(
        max_length=20, choices=MESSAGE_TYPE_CHOICES, default="text", verbose_name="消息类型"
    )
    is_read = models.BooleanField(default=False, verbose_name="是否已读")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="发送时间")

    class Meta:
        verbose_name = "聊天消息"
        verbose_name_plural = "聊天消息"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["from_user", "to_user", "created_at"]),
            models.Index(fields=["group", "created_at"]),
            models.Index(fields=["to_user", "is_read"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(to_user__isnull=False) | models.Q(group__isnull=False),
                name="message_has_recipient",
            ),
        ]

    def __str__(self):
        if self.to_user:
            return f"{self.from_user.username} -> {self.to_user.username}: {self.content[:50]}"
        return f"{self.from_user.username} @ {self.group.name}: {self.content[:50]}"

    def mark_as_read(self):
        """标记为已读"""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=["is_read"])


class UserOnlineStatus(models.Model):
    """用户在线状态"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="online_status",
        verbose_name="用户",
    )
    is_online = models.BooleanField(default=False, verbose_name="是否在线")
    last_seen = models.DateTimeField(auto_now=True, verbose_name="最后在线时间")
    status_text = models.CharField(max_length=100, blank=True, verbose_name="状态文字")

    class Meta:
        verbose_name = "用户在线状态"
        verbose_name_plural = "用户在线状态"

    def __str__(self):
        status = "在线" if self.is_online else "离线"
        return f"{self.user.username} - {status}"

    def set_online(self):
        """设置为在线"""
        self.is_online = True
        self.save(update_fields=["is_online", "last_seen"])

    def set_offline(self):
        """设置为离线"""
        self.is_online = False
        self.save(update_fields=["is_online", "last_seen"])
