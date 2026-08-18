#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""创建测试收藏数据"""
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
from apps.opportunities.models import ExchangeProgram
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 60)
print("[CREATE] Creating Test Bookmark Data")
print("=" * 60)

# 获取用户
user = User.objects.filter(username='Gao').first()
if not user:
    print("[ERROR] User 'Gao' not found!")
    exit(1)

print(f"\n[OK] User: {user.username} (ID: {user.id})")

# 清空现有收藏
old_count = Bookmark.objects.filter(user=user).count()
if old_count > 0:
    Bookmark.objects.filter(user=user).delete()
    print(f"[CLEAN] Deleted {old_count} old bookmarks")

# 获取交换项目
exchanges = ExchangeProgram.objects.all()
print(f"\n[DATA] Database has {exchanges.count()} exchange programs")

if exchanges.count() == 0:
    print("[ERROR] No exchange programs in database!")
    exit(1)

# 创建收藏
created = []
for i, exchange in enumerate(exchanges[:3], 1):  # 收藏前3个
    bookmark = Bookmark.objects.create(
        user=user,
        content_type='exchange',
        object_id=exchange.id
    )
    created.append(bookmark)
    print(f"[OK] Created bookmark {i}: {exchange.title}")

# 验证
final_count = Bookmark.objects.filter(user=user).count()
print(f"\n[RESULT] User now has {final_count} bookmarks")

# 显示收藏详情
print("\n[DETAILS] Bookmark list:")
for i, b in enumerate(created, 1):
    obj = b.content_object
    if obj:
        print(f"  {i}. ID={b.id}, Type={b.content_type}, Object={obj.title}")
    else:
        print(f"  {i}. ID={b.id}, Type={b.content_type}, Object=NOT FOUND")

print("\n" + "=" * 60)
