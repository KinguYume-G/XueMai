#!/usr/bin/env python
"""检查数据库中现有数据数量"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.posts.models import Post
from apps.opportunities.models import ExchangeProgram, Internship
from apps.communities.models import Community
from apps.bookmarks.models import Bookmark
from django.contrib.auth import get_user_model

User = get_user_model()

print("\n" + "="*60)
print("当前数据库数据量统计")
print("="*60)

# 用户
user_count = User.objects.count()
print(f"\n用户 (Users): {user_count} 个")
if user_count > 0:
    for user in User.objects.all()[:5]:
        print(f"  - {user.username} (ID: {user.id}, Email: {user.email})")
    if user_count > 5:
        print(f"  ... 还有 {user_count - 5} 个用户")

# 帖子
post_count = Post.objects.count()
print(f"\n帖子 (Posts): {post_count} 个")
if post_count > 0:
    for post in Post.objects.all()[:3]:
        print(f"  - ID {post.id}: {post.title[:50]}...")

# 交换项目
exchange_count = ExchangeProgram.objects.count()
print(f"\n交换项目 (Exchange Programs): {exchange_count} 个")
if exchange_count > 0:
    for ex in ExchangeProgram.objects.all()[:3]:
        print(f"  - ID {ex.id}: {ex.title[:50]}...")

# 实习
internship_count = Internship.objects.count()
print(f"\n实习 (Internships): {internship_count} 个")
if internship_count > 0:
    for intern in Internship.objects.all()[:3]:
        print(f"  - ID {intern.id}: {intern.title[:50]}...")

# 社区
community_count = Community.objects.count()
print(f"\n社区 (Communities): {community_count} 个")
if community_count > 0:
    for comm in Community.objects.all()[:3]:
        print(f"  - ID {comm.id}: {comm.name[:50]}...")

# 收藏
bookmark_count = Bookmark.objects.count()
print(f"\n收藏 (Bookmarks): {bookmark_count} 个")
if bookmark_count > 0:
    print("\n按用户分组:")
    from django.db.models import Count
    bookmark_by_user = Bookmark.objects.values('user__username').annotate(count=Count('id')).order_by('-count')
    for item in bookmark_by_user[:5]:
        print(f"  - {item['user__username']}: {item['count']} 个收藏")

print("\n" + "="*60)
print("数据统计完成")
print("="*60 + "\n")
