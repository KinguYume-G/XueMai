#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试收藏 API 接口"""
import os
import sys
import django
import requests
from requests.auth import HTTPBasicAuth

# 设置输出编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

print("=" * 60)
print("[API TEST] Testing Bookmark API")
print("=" * 60)

# 获取用户
user = User.objects.filter(username='Gao').first()
if not user:
    print("[ERROR] User 'Gao' not found!")
    exit(1)

print(f"\n[OK] User: {user.username}")

# 生成 JWT Token
refresh = RefreshToken.for_user(user)
access_token = str(refresh.access_token)
print(f"[OK] Generated access token: {access_token[:50]}...")

# 测试 API 接口
api_url = "http://127.0.0.1:8000/api/bookmarks/"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

print(f"\n[REQUEST] GET {api_url}")
print(f"[HEADERS] Authorization: Bearer {access_token[:30]}...")

try:
    response = requests.get(api_url, headers=headers, timeout=10)

    print(f"\n[RESPONSE] Status Code: {response.status_code}")
    print(f"[RESPONSE] Headers: {dict(response.headers)}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n[SUCCESS] Response Data:")
        print(f"  Type: {type(data)}")
        print(f"  Length: {len(data) if isinstance(data, list) else 'N/A'}")
        print(f"  Content: {data}")

        if isinstance(data, list) and len(data) > 0:
            print(f"\n[OK] Received {len(data)} bookmarks")
            for i, item in enumerate(data, 1):
                print(f"  {i}. {item}")
        elif isinstance(data, list) and len(data) == 0:
            print("\n[WARN] Received empty array []")
        else:
            print(f"\n[WARN] Unexpected data type: {type(data)}")
    else:
        print(f"\n[ERROR] Non-200 status code")
        print(f"  Response: {response.text}")

except requests.exceptions.ConnectionError:
    print("\n[ERROR] Cannot connect to server!")
    print("  Make sure Django dev server is running:")
    print("  cd backend && python manage.py runserver")

except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {e}")

print("\n" + "=" * 60)
