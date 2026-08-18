"""
快速获取 JWT Token
用法: python get_token.py [username]
"""

import os
import sys
import django

# 设置 Django 环境
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    django.setup()
except Exception as e:
    print(f"❌ Django 初始化失败: {e}")
    print(f"当前目录: {os.getcwd()}")
    print(f"请确保在 backend 目录下执行此脚本")
    sys.exit(1)

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

def main():
    User = get_user_model()
    
    # 获取命令行参数
    username = sys.argv[1] if len(sys.argv) > 1 else None
    
    # 获取用户
    if username:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            print(f"❌ 用户 '{username}' 不存在\n")
            print("📋 可用用户列表:")
            for u in User.objects.all()[:10]:
                print(f"   - {u.username} {'(超级用户)' if u.is_superuser else ''}")
            sys.exit(1)
    else:
        # 自动选择第一个超级用户
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            user = User.objects.first()
        
        if not user:
            print("❌ 数据库中没有用户，请先创建用户:")
            print("   python manage.py createsuperuser")
            sys.exit(1)
    
    # 生成 Token
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    print("\n" + "="*70)
    print(f"🔑 JWT Token for: {user.username}")
    print("="*70)
    print(f"\n{access_token}\n")
    print("="*70)
    print("\n✅ 复制以上 Token，在测试时使用:")
    print(f'   Authorization: Bearer {access_token[:30]}...\n')
    
    # 保存到文件（可选）
    token_file = os.path.join(BASE_DIR, '.jwt_token')
    try:
        with open(token_file, 'w') as f:
            f.write(access_token)
        print(f"💾 Token 已保存到: {token_file}")
        print(f"   使用: curl -H \"Authorization: Bearer $(cat .jwt_token)\" ...\n")
    except:
        pass
    
    print("="*70 + "\n")

if __name__ == "__main__":
    main()