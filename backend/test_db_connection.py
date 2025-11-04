"""
测试数据库连接
运行：python test_db_connection.py
"""
import os
import sys
import django

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from django.db import connection


def test_connection():
    """测试数据库连接"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            row = cursor.fetchone()
            print("✓ 数据库连接成功")
            print(f"数据库版本: {row[0]}")
            
            # 测试表是否存在
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                LIMIT 5;
            """)
            tables = cursor.fetchall()
            if tables:
                print(f"\n已存在的表（前5个）:")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("\n提示：数据库中还没有表，请运行 'python manage.py migrate'")
                
    except Exception as e:
        print(f"✗ 数据库连接失败")
        print(f"错误信息: {e}")
        print("\n请检查：")
        print("1. DATABASE_URL 环境变量是否正确")
        print("2. 数据库服务是否运行")
        print("3. 网络连接是否正常")
        print("4. Supabase连接必须包含 ?sslmode=require")


if __name__ == "__main__":
    test_connection()

