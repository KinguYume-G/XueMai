"""
正式导入完整薪资数据到RAG系统（150条）
Import Full Salary Data to RAG System

Author: UniPulse Asia Team
Date: 2025-11-29
"""

import os
import sys
import json
import django
from pathlib import Path
from datetime import datetime

# Django setup
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.ai.services.rag_engine import RAGEngine
from apps.ai.models import AIDocument, AIChunk, AIEmbedding


def import_salary_full_data():
    """导入完整薪资数据"""
    
    print("="*80)
    print("📥 正式导入完整薪资数据（150条）")
    print("="*80)
    
    # 读取完整数据
    data_file = Path(__file__).parent.parent / 'backend' / 'data' / 'crawled' / 'salary_full.json'
    
    if not data_file.exists():
        print(f"❌ 文件不存在：{data_file}")
        return False
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    salaries = data['salaries']
    print(f"\n📦 读取到 {len(salaries)} 条薪资数据")
    
    # 初始化RAG引擎
    rag_engine = RAGEngine()
    
    try:
        # 1. 删除旧数据（包括测试数据）
        print("\n🗑️  删除旧的薪资数据...")
        old_docs = AIDocument.objects.filter(doc_type='salary')
        old_count = old_docs.count()
        
        if old_count > 0:
            # 删除相关的chunks和embeddings
            old_chunks = AIChunk.objects.filter(document__in=old_docs)
            old_embeddings_count = AIEmbedding.objects.filter(chunk__in=old_chunks).count()
            AIEmbedding.objects.filter(chunk__in=old_chunks).delete()
            old_chunks.delete()
            old_docs.delete()
            print(f"   已删除 {old_count} 个文档, {old_embeddings_count} 个embeddings")
        
        # 2. 导入新数据
        print("\n📥 导入完整薪资数据...")
        print(f"   方案A（政府统计）：{data['stats']['method_a_count']}条")
        print(f"   方案B（PayScale）：{data['stats']['method_b_count']}条")
        print(f"   方案C（手动收集）：{data['stats']['method_c_count']}条")
        print()
        
        imported_count = 0
        chunk_count = 0
        embedding_count = 0
        
        for idx, salary_data in enumerate(salaries, 1):
            try:
                # 构建结构化内容
                content = f"""
职位名称：{salary_data['position']}
所属行业：{salary_data['industry']}
薪资范围：{salary_data['salary_min']:,} - {salary_data['salary_max']:,} {salary_data['currency']} / {salary_data['period']}
经验要求：{salary_data['experience_level']}
工作地点：{salary_data['location']}

职位描述：
{salary_data['job_description']}

技能要求：
{', '.join(salary_data['required_skills'])}

学历要求：
{salary_data['education']}

福利待遇：
{salary_data['benefits']}

数据来源：{salary_data['source']}
采集方式：{salary_data['collection_method']}
数据年份：{salary_data['data_year']}
""".strip()
                
                # 元数据
                metadata = {
                    "position": salary_data['position'],
                    "industry": salary_data['industry'],
                    "salary_min": salary_data['salary_min'],
                    "salary_max": salary_data['salary_max'],
                    "currency": salary_data['currency'],
                    "period": salary_data['period'],
                    "experience_level": salary_data['experience_level'],
                    "location": salary_data['location'],
                    "source": salary_data['source'],
                    "data_year": salary_data['data_year'],
                    "required_skills": salary_data['required_skills'],
                    "education": salary_data['education'],
                    "benefits": salary_data['benefits'],
                    "collection_method": salary_data['collection_method'],
                    "version": "full",
                    "data_type": "salary",
                    "import_source": "salary_full"
                }
                
                # 创建AIDocument
                document = AIDocument.objects.create(
                    title=f"{salary_data['position']} - {salary_data['industry']}",
                    content=content,
                    doc_type='salary',
                    source_url=salary_data['source'],
                    metadata=metadata
                )
                
                imported_count += 1
                
                # 使用RAG引擎的text_splitter分块
                chunks = rag_engine.text_splitter.split_text(content)
                
                for j, chunk_text in enumerate(chunks):
                    # 创建chunk
                    chunk = AIChunk.objects.create(
                        document=document,
                        content=chunk_text,
                        chunk_index=j,
                        chunk_metadata={
                            'word_count': len(chunk_text),
                            'source': 'salary_full',
                            'position': salary_data['position'],
                            'industry': salary_data['industry'],
                            'location': salary_data['location']
                        }
                    )
                    
                    # 生成embedding
                    embedding_vector = rag_engine.embeddings.embed_query(chunk_text)
                    
                    AIEmbedding.objects.create(
                        chunk=chunk,
                        embedding_vector=embedding_vector,
                        embedding_model='nomic-embed-text'
                    )
                    
                    chunk_count += 1
                    embedding_count += 1
                
                # 每50条显示进度
                if idx % 50 == 0:
                    print(f"   进度：{idx}/{len(salaries)} ({idx/len(salaries)*100:.1f}%)")
                
            except Exception as e:
                print(f"   ❌ [{idx}/{len(salaries)}] {salary_data.get('position', 'Unknown')} 导入失败：{str(e)}")
                continue
        
        print(f"\n   ✅ 导入完成：{imported_count}/{len(salaries)}")
        
        # 3. 验证数据完整性
        print("\n📊 数据完整性验证：")
        salary_docs = AIDocument.objects.filter(metadata__import_source='salary_full').count()
        salary_chunks = AIChunk.objects.filter(chunk_metadata__source='salary_full').count()
        salary_embeddings = AIEmbedding.objects.filter(chunk__chunk_metadata__source='salary_full').count()
        
        print(f"   文档数：{salary_docs}")
        print(f"   Chunks数：{salary_chunks}")
        print(f"   Embeddings数：{salary_embeddings}")
        print(f"   完整性：{'✅ 通过' if salary_chunks == salary_embeddings else '⚠️  不一致'}")
        
        print("\n" + "="*80)
        print("✅ 薪资数据已成功导入RAG系统！")
        print("="*80)
        print(f"📊 导入统计：")
        print(f"   - 文档数：{imported_count}")
        print(f"   - Chunks数：{chunk_count}")
        print(f"   - Embeddings数：{embedding_count}")
        print(f"   - 数据类型：salary")
        print(f"   - 数据版本：full (150条)")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 导入失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = import_salary_full_data()
    sys.exit(0 if success else 1)







