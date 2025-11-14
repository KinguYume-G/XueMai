#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""清理测试数据 - 方案A（激进清理）"""
import os
import sys
import django

# 设置标准输出编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.users.models import User
from apps.posts.models import Post
from apps.opportunities.models import ExchangeProgram, Internship
from apps.communities.models import Community
from apps.bookmarks.models import Bookmark
from django.db.models import Q

print("\n" + "="*80)
print("学脉平台 - 数据清理脚本（方案A：激进清理）")
print("="*80)

print("\n[警告] 此操作将删除以下数据：")
print("  - 2 个测试用户 (alice, Jeffrey)")
print("  - 79 个测试帖子（全部帖子）")
print("  - 15 个测试实习（全部实习）")
print("  - 4 个交换项目（全部交换项目）")
print("  - 所有相关收藏")
print("\n保留数据：")
print("  - 11 个生产用户")
print("  - 2 个社区（游戏爱好者社区、APU摄影社）")

# 统计删除前的数据
print("\n" + "="*80)
print("【删除前数据统计】")
print("="*80)
print(f"用户: {User.objects.count()} 个")
print(f"帖子: {Post.objects.count()} 个")
print(f"交换项目: {ExchangeProgram.objects.count()} 个")
print(f"实习: {Internship.objects.count()} 个")
print(f"社区: {Community.objects.count()} 个")
print(f"收藏: {Bookmark.objects.count()} 个")

# 开始清理
print("\n" + "="*80)
print("【开始清理操作】")
print("="*80)

# 步骤 1: 删除所有收藏
print("\n[步骤 1] 删除所有收藏...")
bookmark_count = Bookmark.objects.count()
Bookmark.objects.all().delete()
print(f"[OK] 已删除 {bookmark_count} 个收藏")

# 步骤 2: 删除所有帖子
print("\n[步骤 2] 删除所有帖子...")
post_count = Post.objects.count()
Post.objects.all().delete()
print(f"[OK] 已删除 {post_count} 个帖子")

# 步骤 3: 删除所有交换项目
print("\n[步骤 3] 删除所有交换项目...")
exchange_count = ExchangeProgram.objects.count()
ExchangeProgram.objects.all().delete()
print(f"[OK] 已删除 {exchange_count} 个交换项目")

# 步骤 4: 删除所有实习
print("\n[步骤 4] 删除所有实习...")
internship_count = Internship.objects.count()
Internship.objects.all().delete()
print(f"[OK] 已删除 {internship_count} 个实习")

# 步骤 5: 删除测试用户
print("\n[步骤 5] 删除测试用户...")
test_users = User.objects.filter(Q(username='alice') | Q(username='Alice') | Q(username='Jeffrey') | Q(username='JEFFREY'))
test_user_count = test_users.count()
if test_user_count > 0:
    for user in test_users:
        print(f"  - 删除用户: {user.username} (ID: {user.id})")
    test_users.delete()
    print(f"[OK] 已删除 {test_user_count} 个测试用户")
else:
    print("[INFO] 未找到测试用户")

# 统计删除后的数据
print("\n" + "="*80)
print("【删除后数据统计】")
print("="*80)
print(f"用户: {User.objects.count()} 个")
print(f"帖子: {Post.objects.count()} 个")
print(f"交换项目: {ExchangeProgram.objects.count()} 个")
print(f"实习: {Internship.objects.count()} 个")
print(f"社区: {Community.objects.count()} 个")
print(f"收藏: {Bookmark.objects.count()} 个")

# 显示剩余的生产数据
print("\n" + "="*80)
print("【剩余生产数据】")
print("="*80)

print("\n生产用户列表:")
for user in User.objects.all():
    print(f"  - {user.username} (ID: {user.id}, Email: {user.email})")

print("\n生产社区列表:")
for community in Community.objects.all():
    print(f"  - {community.name} (ID: {community.id}, 成员: {community.members})")

# 汇总报告
print("\n" + "="*80)
print("【清理汇总报告】")
print("="*80)
print(f"\n已删除:")
print(f"  - 收藏: {bookmark_count} 个")
print(f"  - 帖子: {post_count} 个")
print(f"  - 交换项目: {exchange_count} 个")
print(f"  - 实习: {internship_count} 个")
print(f"  - 测试用户: {test_user_count} 个")

print(f"\n保留:")
print(f"  - 生产用户: {User.objects.count()} 个")
print(f"  - 社区: {Community.objects.count()} 个")

print("\n" + "="*80)
print("[SUCCESS] 数据清理完成！数据库已准备好创建真实数据。")
print("="*80 + "\n")
