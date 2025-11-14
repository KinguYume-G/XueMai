#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""创建收藏功能测试数据"""
import os
import sys
import django

# 设置标准输出编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.bookmarks.models import Bookmark
from apps.posts.models import Post
from apps.opportunities.models import ExchangeProgram, Internship
from apps.communities.models import Community
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()

print("\n" + "="*70)
print("学脉平台 - 创建收藏功能测试数据")
print("="*70)

# ===== 步骤 1: 获取当前登录用户 =====
print("\n[步骤 1] 获取当前用户...")
# 先尝试找 JEFFREY 用户，如果没有就用 Xing
user = User.objects.filter(username='JEFFREY').first()
if not user:
    user = User.objects.filter(username='Xing').first()
if not user:
    user = User.objects.first()
print(f"[OK] 当前用户: {user.username} (ID: {user.id}, Email: {user.email})")

# ===== 步骤 2: 检查和创建帖子 =====
print("\n[步骤 2] 检查和创建帖子...")
current_posts = Post.objects.count()
print(f"当前有 {current_posts} 个帖子")
print(f"[OK] 帖子数据充足，跳过创建")

# ===== 步骤 3: 检查和创建交换项目 =====
print("\n[步骤 3] 检查和创建交换项目...")
current_exchanges = ExchangeProgram.objects.count()
print(f"当前有 {current_exchanges} 个交换项目")
print(f"[OK] 交换项目数据充足，跳过创建")

# ===== 步骤 4: 检查和创建实习 =====
print("\n[步骤 4] 检查和创建实习...")
current_internships = Internship.objects.count()
print(f"当前有 {current_internships} 个实习")
print(f"[OK] 实习数据充足，跳过创建")

# ===== 步骤 5: 检查和创建社区 =====
print("\n[步骤 5] 检查和创建社区...")
current_communities = Community.objects.count()
print(f"当前有 {current_communities} 个社区")

if current_communities < 2:
    comm1 = Community.objects.create(
        name="游戏爱好者社区",
        description="分享游戏心得，组队开黑，电竞交流",
        members=512,
        activity_rate=0.87,
        category='interest',
        created_by=user
    )
    print(f"[OK] 创建了社区: {comm1.name} (ID: {comm1.id})")

    comm2 = Community.objects.create(
        name="APU摄影社",
        description="摄影技巧交流，作品分享，外拍活动",
        members=325,
        activity_rate=0.73,
        category='interest',
        created_by=user
    )
    print(f"[OK] 创建了社区: {comm2.name} (ID: {comm2.id})")
else:
    print(f"[OK] 社区数据充足，跳过创建")

# ===== 步骤 6: 创建收藏 =====
print("\n[步骤 6] 创建收藏...")
Bookmark.objects.filter(user=user).delete()
print("[OK] 已清空用户现有收藏")

bookmark_count = 0

# 收藏帖子
posts_to_bookmark = Post.objects.all()[:2]
for post in posts_to_bookmark:
    Bookmark.objects.create(
        user=user,
        content_type='post',
        object_id=post.id
    )
    bookmark_count += 1
    print(f"[OK] 收藏了帖子: ID {post.id}")

# 收藏交换项目
exchanges_to_bookmark = ExchangeProgram.objects.all()[:2]
for exchange in exchanges_to_bookmark:
    Bookmark.objects.create(
        user=user,
        content_type='exchange',
        object_id=exchange.id
    )
    bookmark_count += 1
    print(f"[OK] 收藏了交换项目: {exchange.title}")

# 收藏实习
internships_to_bookmark = Internship.objects.all()[:2]
for internship in internships_to_bookmark:
    Bookmark.objects.create(
        user=user,
        content_type='internship',
        object_id=internship.id
    )
    bookmark_count += 1
    print(f"[OK] 收藏了实习: {internship.title}")

# 收藏社区
communities_to_bookmark = Community.objects.all()[:2]
for community in communities_to_bookmark:
    Bookmark.objects.create(
        user=user,
        content_type='community',
        object_id=community.id
    )
    bookmark_count += 1
    print(f"[OK] 收藏了社区: {community.name}")

# ===== 最终统计 =====
print("\n" + "="*70)
print("最终统计")
print("="*70)
print(f"\n用户: {user.username}")
print(f"总收藏数: {bookmark_count} 个")
print(f"  - 帖子: {Bookmark.objects.filter(user=user, content_type='post').count()} 个")
print(f"  - 交换项目: {Bookmark.objects.filter(user=user, content_type='exchange').count()} 个")
print(f"  - 实习: {Bookmark.objects.filter(user=user, content_type='internship').count()} 个")
print(f"  - 社区: {Bookmark.objects.filter(user=user, content_type='community').count()} 个")

print("\n" + "="*70)
print("[SUCCESS] 数据创建完成！请刷新前端页面查看效果。")
print("="*70 + "\n")
