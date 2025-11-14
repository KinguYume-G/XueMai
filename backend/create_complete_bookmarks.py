#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""创建完整的测试收藏数据（所有类型）"""
import os
import sys
import django

# 设置输出编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.bookmarks.models import Bookmark
from apps.feed.models import Post
from apps.opportunities.models import ExchangeProgram, Internship
from apps.communities.models import Community
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 60)
print("[COMPLETE] Creating Full Test Bookmark Data")
print("=" * 60)

# 获取用户 Gao
user = User.objects.filter(username='Gao').first()
if not user:
    print("[WARN] User 'Gao' not found, using first user")
    user = User.objects.first()

if not user:
    print("[ERROR] No users in database!")
    exit(1)

print(f"\n[OK] Current User: {user.username} (ID: {user.id})")

# 清空现有收藏
old_count = Bookmark.objects.filter(user=user).count()
if old_count > 0:
    Bookmark.objects.filter(user=user).delete()
    print(f"[CLEAN] Deleted {old_count} old bookmarks")

# ===== 1. 帖子 =====
print("\n" + "=" * 60)
print("[STEP 1] Posts")
print("=" * 60)
posts = Post.objects.all()
print(f"[CHECK] Database has {posts.count()} posts")

if posts.count() == 0:
    print("[CREATE] Creating test posts...")
    Post.objects.create(
        author=user,
        title="AI Paper Writing Tips",
        content="Sharing my experience on writing AI research papers...",
        likes_count=156,
        comments_count=23
    )
    Post.objects.create(
        author=user,
        title="Internship Experience in Malaysia",
        content="Sharing my experience finding internships in Malaysia...",
        likes_count=234,
        comments_count=45
    )
    posts = Post.objects.all()
    print(f"[OK] Created {posts.count()} test posts")

# 创建帖子收藏
post_bookmarks = 0
for post in posts[:2]:
    bookmark = Bookmark.objects.create(
        user=user,
        content_type='post',
        object_id=post.id
    )
    print(f"[OK] Bookmarked post: ID={post.id}, title={post.title[:40]}...")
    post_bookmarks += 1

# ===== 2. 交换项目 =====
print("\n" + "=" * 60)
print("[STEP 2] Exchange Programs")
print("=" * 60)
exchanges = ExchangeProgram.objects.all()
print(f"[CHECK] Database has {exchanges.count()} exchange programs")

if exchanges.count() == 0:
    print("[ERROR] No exchange programs in database!")
else:
    # 创建交换项目收藏
    exchange_bookmarks = 0
    for exchange in exchanges[:2]:
        bookmark = Bookmark.objects.create(
            user=user,
            content_type='exchange',
            object_id=exchange.id
        )
        print(f"[OK] Bookmarked exchange: ID={exchange.id}, title={exchange.title}")
        exchange_bookmarks += 1

# ===== 3. 实习 =====
print("\n" + "=" * 60)
print("[STEP 3] Internships")
print("=" * 60)
internships = Internship.objects.all()
print(f"[CHECK] Database has {internships.count()} internships")

if internships.count() == 0:
    print("[CREATE] Creating test internships...")
    Internship.objects.create(
        title="Frontend Developer Intern",
        company="Tencent",
        location="Shenzhen",
        salary_min=5000,
        salary_max=8000,
        description="Responsible for frontend development...",
        requirements="Familiar with React, Vue...",
        is_remote=True,
        posted_by=user
    )
    Internship.objects.create(
        title="AI Algorithm Intern",
        company="Alibaba",
        location="Hangzhou",
        salary_min=6000,
        salary_max=10000,
        description="Responsible for AI algorithm R&D...",
        requirements="Familiar with Python, TensorFlow...",
        is_remote=False,
        posted_by=user
    )
    internships = Internship.objects.all()
    print(f"[OK] Created {internships.count()} test internships")

# 创建实习收藏
internship_bookmarks = 0
for internship in internships[:2]:
    bookmark = Bookmark.objects.create(
        user=user,
        content_type='internship',
        object_id=internship.id
    )
    print(f"[OK] Bookmarked internship: ID={internship.id}, title={internship.title}")
    internship_bookmarks += 1

# ===== 4. 社区 =====
print("\n" + "=" * 60)
print("[STEP 4] Communities")
print("=" * 60)
communities = Community.objects.all()
print(f"[CHECK] Database has {communities.count()} communities")

if communities.count() == 0:
    print("[CREATE] Creating test communities...")
    Community.objects.create(
        name="Gaming Community",
        description="Share gaming experiences, team up, esports discussion",
        member_count=512,
        active_rate=87,
        creator=user
    )
    Community.objects.create(
        name="APU Basketball Club",
        description="Basketball lovers, schedule sharing, outdoor activities",
        member_count=325,
        active_rate=73,
        creator=user
    )
    communities = Community.objects.all()
    print(f"[OK] Created {communities.count()} test communities")

# 创建社区收藏
community_bookmarks = 0
for community in communities[:2]:
    bookmark = Bookmark.objects.create(
        user=user,
        content_type='community',
        object_id=community.id
    )
    print(f"[OK] Bookmarked community: ID={community.id}, name={community.name}")
    community_bookmarks += 1

# ===== 最终统计 =====
print("\n" + "=" * 60)
print("[FINAL] Statistics")
print("=" * 60)

total = Bookmark.objects.filter(user=user).count()
post_count = Bookmark.objects.filter(user=user, content_type='post').count()
exchange_count = Bookmark.objects.filter(user=user, content_type='exchange').count()
internship_count = Bookmark.objects.filter(user=user, content_type='internship').count()
community_count = Bookmark.objects.filter(user=user, content_type='community').count()

print(f"\nTotal Bookmarks: {total}")
print(f"  - Posts: {post_count}")
print(f"  - Exchange Programs: {exchange_count}")
print(f"  - Internships: {internship_count}")
print(f"  - Communities: {community_count}")

print("\n[DETAILS] All bookmarks:")
for b in Bookmark.objects.filter(user=user).order_by('content_type', '-created_at'):
    print(f"  - ID={b.id}, type={b.content_type}, object_id={b.object_id}")

print("\n" + "=" * 60)
print("[SUCCESS] Complete! Ready to test in browser.")
print("=" * 60)
