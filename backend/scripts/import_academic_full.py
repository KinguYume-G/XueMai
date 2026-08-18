"""
正式导入学术数据到RAG系统
将academic_full.json导入到Django数据库
"""

import os
import sys
import django
import json
from pathlib import Path
from datetime import datetime

# 设置Django环境
sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.ai.models import AIDocument, AIChunk, AIEmbedding
from apps.ai.services.rag_engine import RAGEngine


def import_academic_data():
    """导入学术数据"""
    print("=" * 80)
    print("📥 正式导入学术数据到RAG系统")
    print("=" * 80)
    
    # 1. 加载数据
    file_path = Path(__file__).parent.parent / 'backend' / 'data' / 'crawled' / 'academic_full.json'
    
    print(f"\n📂 加载数据：{file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ 成功加载 {len(data)} 条记录")
    
    # 2. 初始化RAG引擎
    rag_engine = RAGEngine()
    print(f"\n✅ RAG引擎初始化完成")
    
    # 3. 导入数据
    print(f"\n{'='*80}")
    print(f"开始导入...")
    print(f"{'='*80}\n")
    
    total_docs = 0
    total_chunks = 0
    total_embeddings = 0
    failed = 0
    
    for i, item in enumerate(data, 1):
        try:
            print(f"[{i}/{len(data)}] 处理: {item['title'][:50]}...")
            
            # 创建AIDocument
            doc = AIDocument.objects.create(
                doc_type='other',
                title=item['title'],
                content=item['content'],
                source_url=item.get('source_url', ''),
                metadata={
                    'category': item.get('category', 'academic'),
                    'subcategory': item.get('subcategory', ''),
                    'scraped_at': item.get('scraped_at', ''),
                    'source': 'purdue_owl',
                    'content_length': item.get('content_length', 0),
                    'word_count': item.get('word_count', 0)
                },
                is_active=True
            )
            total_docs += 1
            
            # 文本分块（chunk_size=500）
            chunks = rag_engine.text_splitter.split_text(item['content'])
            chunk_count = len(chunks)
            
            # 生成向量
            embeddings = rag_engine.embeddings.embed_documents(chunks)
            embedding_count = len(embeddings)
            
            # 保存chunks和embeddings
            for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                chunk = AIChunk.objects.create(
                    document=doc,
                    content=chunk_text,
                    chunk_index=idx,
                    chunk_metadata={
                        'chunk_size': len(chunk_text),
                        'source': 'academic_import'
                    }
                )
                total_chunks += 1
                
                AIEmbedding.objects.create(
                    chunk=chunk,
                    embedding_vector=embedding,
                    embedding_model='nomic-embed-text'
                )
                total_embeddings += 1
            
            print(f"  ✅ 完成：{chunk_count} chunks, {embedding_count} embeddings")
            
        except Exception as e:
            print(f"  ❌ 失败：{e}")
            failed += 1
            import traceback
            traceback.print_exc()
    
    # 4. 验证数据完整性
    print(f"\n{'='*80}")
    print(f"数据完整性验证")
    print(f"{'='*80}")
    
    actual_chunks = AIChunk.objects.filter(
        chunk_metadata__source='academic_import'
    ).count()
    
    actual_embeddings = AIEmbedding.objects.filter(
        chunk__chunk_metadata__source='academic_import'
    ).count()
    
    print(f"\n数据库统计:")
    print(f"  文档数：{total_docs}")
    print(f"  Chunks数：{total_chunks}")
    print(f"  Embeddings数：{total_embeddings}")
    print(f"\n数据库验证:")
    print(f"  实际Chunks：{actual_chunks}")
    print(f"  实际Embeddings：{actual_embeddings}")
    
    if total_chunks == actual_embeddings and actual_chunks == actual_embeddings:
        print(f"\n✅ 数据完整性验证通过！")
        print(f"   Chunks数量 = Embeddings数量 = {total_chunks}")
    else:
        print(f"\n⚠️  数据完整性检查失败")
        print(f"   预期：{total_chunks}")
        print(f"   实际Chunks：{actual_chunks}")
        print(f"   实际Embeddings：{actual_embeddings}")
    
    # 5. 生成最终报告
    print(f"\n{'='*80}")
    print(f"📊 导入完成统计")
    print(f"{'='*80}")
    print(f"\n✅ 成功导入：")
    print(f"   - {total_docs} 个文档")
    print(f"   - {total_chunks} 个chunks")
    print(f"   - {total_embeddings} 个embeddings")
    
    if failed > 0:
        print(f"\n❌ 失败：{failed} 个文档")
    
    # 按分类统计
    print(f"\n按分类统计:")
    for category in ['apa_format', 'mla_format', 'chicago_format', 'ieee_format']:
        count = AIDocument.objects.filter(
            metadata__subcategory=category
        ).count()
        if count > 0:
            print(f"  - {category}: {count} 个文档")
    
    print(f"\n{'='*80}")
    print(f"✅ 指令1-5完成！学术数据已成功导入RAG系统")
    print(f"{'='*80}")
    
    return {
        'docs': total_docs,
        'chunks': total_chunks,
        'embeddings': total_embeddings,
        'failed': failed
    }


if __name__ == '__main__':
    result = import_academic_data()
    
    print(f"\n下一步建议：")
    print(f"1. 使用Django shell验证数据")
    print(f"2. 测试学术AI助手功能")
    print(f"3. 继续爬取其他类型数据（简历模板、面试题等）")

