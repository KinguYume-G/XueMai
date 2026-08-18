"""
新闻数据正式导入RAG系统
从news_full.json导入所有创业新闻到RAG系统
"""

import sys
import json
import os
import django
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'backend'))

# 配置Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# 导入RAG引擎
from apps.ai.services.rag_engine import RAGEngine
from apps.ai.models import AIDocument, AIChunk, AIEmbedding


def load_news_data(file_path: str):
    """加载新闻数据"""
    print(f"加载数据: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    articles = data.get('articles', data if isinstance(data, list) else [])
    print(f"✅ 加载了 {len(articles)} 篇新闻")
    
    return articles, data.get('metadata', {})


def import_to_rag(articles: list, rag_engine: RAGEngine):
    """导入新闻到RAG系统"""
    print(f"\n{'='*80}")
    print(f"开始导入 {len(articles)} 篇新闻到RAG...")
    print(f"{'='*80}\n")
    
    imported_count = 0
    total_chunks = 0
    total_embeddings = 0
    failed = 0
    
    for i, article in enumerate(articles):
        try:
            # 创建AIDocument
            doc = AIDocument.objects.create(
                title=article.get('title', 'Untitled'),
                content=article.get('content', ''),
                source_url=article.get('link', ''),
                doc_type='other',
                metadata={
                    'summary': article.get('summary', ''),
                    'published': article.get('published', ''),
                    'author': article.get('author', ''),
                    'source': article.get('source', ''),
                    'category': article.get('category', 'startup'),
                    'subcategory': article.get('subcategory', 'news'),
                    'data_type': 'news_article',
                    'import_source': 'news_full'
                }
            )
            
            # 使用RAG引擎分块
            text = article.get('content', '')
            chunks = rag_engine.text_splitter.split_text(text)
            
            chunk_count = 0
            for j, chunk_text in enumerate(chunks):
                # 创建chunk
                chunk = AIChunk.objects.create(
                    document=doc,
                    content=chunk_text,
                    chunk_index=j,
                    chunk_metadata={
                        'word_count': len(chunk_text),
                        'source': 'news_full'
                    }
                )
                chunk_count += 1
                total_chunks += 1
                
                # 生成embedding
                embedding_vector = rag_engine.embeddings.embed_query(chunk_text)
                
                AIEmbedding.objects.create(
                    chunk=chunk,
                    embedding_vector=embedding_vector,
                    embedding_model='nomic-embed-text'
                )
                total_embeddings += 1
            
            imported_count += 1
            print(f"  ✅ [{i+1}/{len(articles)}] {article['title'][:50]}... ({chunk_count} chunks)")
            
        except Exception as e:
            print(f"  ❌ [{i+1}/{len(articles)}] 导入失败: {e}")
            failed += 1
    
    print(f"\n✅ 成功导入 {imported_count}/{len(articles)} 篇新闻")
    print(f"   总Chunks: {total_chunks}")
    print(f"   总Embeddings: {total_embeddings}")
    
    if failed > 0:
        print(f"\n❌ 失败: {failed} 篇")
    
    return imported_count, total_chunks, total_embeddings


def verify_data_integrity():
    """验证数据完整性"""
    print(f"\n{'='*80}")
    print("验证数据完整性")
    print(f"{'='*80}\n")
    
    # 查询新闻类型的文档
    from django.db.models import Q
    news_docs = AIDocument.objects.filter(
        Q(doc_type='other') & Q(metadata__import_source='news_full')
    )
    
    total_chunks = AIChunk.objects.filter(
        chunk_metadata__source='news_full'
    ).count()
    
    total_embeddings = AIEmbedding.objects.filter(
        chunk__chunk_metadata__source='news_full'
    ).count()
    
    print(f"新闻文档数: {news_docs.count()}")
    print(f"新闻Chunks数: {total_chunks}")
    print(f"新闻Embeddings数: {total_embeddings}")
    
    if total_chunks == total_embeddings:
        print(f"\n✅ 数据完整性验证通过 (chunks == embeddings)")
        return True
    else:
        print(f"\n❌ 数据不完整 (chunks={total_chunks}, embeddings={total_embeddings})")
        return False


def main():
    """主函数"""
    print("=" * 80)
    print("📰 新闻数据正式导入RAG系统")
    print("=" * 80)
    
    # 1. 加载数据
    file_path = Path(__file__).parent.parent / 'backend' / 'backend' / 'data' / 'crawled' / 'news_full.json'
    articles, metadata = load_news_data(str(file_path))
    
    if not articles:
        print("\n❌ 没有数据可导入")
        sys.exit(1)
    
    # 2. 初始化RAG引擎
    print("\n初始化RAG引擎...")
    rag_engine = RAGEngine()
    
    # 3. 导入数据
    imported_count, total_chunks, total_embeddings = import_to_rag(articles, rag_engine)
    
    # 4. 验证数据完整性
    integrity_ok = verify_data_integrity()
    
    # 5. 生成报告
    print(f"\n{'='*80}")
    print("📊 导入完成统计")
    print(f"{'='*80}")
    
    print(f"\n✅ 成功导入：")
    print(f"   - {imported_count} 个文档")
    print(f"   - {total_chunks} 个chunks")
    print(f"   - {total_embeddings} 个embeddings")
    
    print(f"\n数据完整性: {'✅ 通过' if integrity_ok else '❌ 失败'}")
    
    # 6. 输出下一步
    print(f"\n{'='*80}")
    print("✅ 新闻数据已成功导入RAG系统！")
    print("=" * 80)
    print("\n下一步:")
    print("  - 可以在智能对话中询问创业新闻相关问题")
    print("  - 例如：'最近有哪些AI创业公司获得融资？'")
    print("=" * 80)


if __name__ == '__main__':
    main()

