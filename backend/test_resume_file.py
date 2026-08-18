"""
测试高星简历.docx文件处理

用于诊断为什么这个特定文件无法提取内容
"""
import sys
import os
from io import BytesIO
from pathlib import Path

# 添加项目路径
sys.path.insert(0, r'C:\Users\hp\Desktop\UniPulse Asia\XueMai\backend')

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
import django
django.setup()

from apps.ai.services.file_processor import FileProcessor
from django.core.files.storage import default_storage

print("=" * 60)
print("诊断高星简历.docx处理问题")
print("=" * 60)

# 从存储中读取文件
file_path = "uploads/19/52588397_高星简历_2XEanA8.docx"

try:
    print(f"\n1. 检查文件是否存在...")
    if default_storage.exists(file_path):
        print(f"   ✅ 文件存在: {file_path}")
        
        # 获取文件大小
        file_size = default_storage.size(file_path)
        print(f"   文件大小: {file_size} bytes")
        
        # 读取文件
        print(f"\n2. 读取文件内容...")
        with default_storage.open(file_path, 'rb') as f:
            file_bytes = f.read()
            print(f"   读取字节数: {len(file_bytes)}")
            
            # 检查文件头（DOCX是ZIP格式，应该以PK开头）
            file_header = file_bytes[:4]
            print(f"   文件头: {file_header}")
            if file_header[:2] == b'PK':
                print(f"   ✅ 文件头正确（ZIP/DOCX格式）")
            else:
                print(f"   ❌ 文件头异常！不是标准DOCX格式")
            
            # 尝试处理
            print(f"\n3. 尝试提取内容...")
            stream = BytesIO(file_bytes)
            result = FileProcessor.process_file_from_stream(stream, 'docx')
            
            print(f"\n4. 处理结果:")
            print(f"   提取文本长度: {len(result.get('extracted_text', ''))}")
            print(f"   段落数: {result.get('paragraph_count', 0)}")
            print(f"   表格数: {result.get('table_count', 0)}")
            
            if result.get('extracted_text'):
                print(f"\n   ✅ 内容提取成功！")
                print(f"   前200字符: {result['extracted_text'][:200]}")
            else:
                print(f"\n   ❌ 内容为空！")
                
    else:
        print(f"   ❌ 文件不存在: {file_path}")
        
except Exception as e:
    print(f"\n❌ 处理失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
