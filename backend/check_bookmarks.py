#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查收藏数据的诊断脚本"""
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
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 60)
print("[BOOKMARK] Diagnosis Report")
print("=" * 60)

# 获取当前用户（Gao）
user = User.objects.filter(username='Gao').first()
if not user:
    print("[WARNING] User 'Gao' not found, using first user")
    user = User.objects.first()

if not user:
    print("[ERROR] No users in database!")
    exit(1)

print(f"\n[OK] Current User: {user.username} (ID: {user.id})")
print(f"     Email: {user.email}")

# 检查收藏数量
count = Bookmark.objects.filter(user=user).count()
print(f"\n[DATA] User has {count} bookmarks")

# 查看所有收藏
if count > 0:
    print("\nBookmark Details:")
    bookmarks = Bookmark.objects.filter(user=user).order_by('-created_at')
    for i, b in enumerate(bookmarks, 1):
        print(f"  {i}. {b.content_type} (ID: {b.object_id}) - Created: {b.created_at}")

    # 检查关联对象是否存在
    print("\n[CHECK] Validating related objects:")
    for b in bookmarks:
        obj = b.content_object
        if obj:
            title = getattr(obj, 'title', getattr(obj, 'name', 'N/A'))
            print(f"  [OK] {b.content_type} #{b.object_id}: {title}")
        else:
            print(f"  [ERROR] {b.content_type} #{b.object_id}: Object does not exist!")
else:
    print("\n[WARN] User has NO bookmarks")

# 检查交换项目数量
from apps.opportunities.models import ExchangeProgram
exchange_count = ExchangeProgram.objects.count()
print(f"\n[DATA] Database has {exchange_count} exchange programs")

print("\n" + "=" * 60)
