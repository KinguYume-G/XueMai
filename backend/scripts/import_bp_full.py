"""
商业计划书模板正式导入RAG系统
从bp_test.json导入所有BP模板到RAG系统
"""

import sys
import os
import django
from pathlib import Path
import json

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'backend'))

# 配置Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# 导入RAG引擎和模型
from apps.ai.services.rag_engine import RAGEngine
from apps.ai.models import AIDocument, AIChunk, AIEmbedding


def import_bp_templates():
    """导入BP模板到RAG"""
    print("=" * 80)
    print("📄 商业计划书模板正式导入RAG")
    print("=" * 80)
    
    # 加载数据
    file_path = Path(__file__).parent.parent / 'backend' / 'data' / 'crawled' / 'bp_test.json'
    print(f"\n加载数据: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    templates = data.get('templates', [])
    print(f"✅ 加载了 {len(templates)} 个BP模板")
    
    # 初始化RAG引擎
    rag_engine = RAGEngine()
    
    # 导入
    print(f"\n{'='*80}")
    print(f"开始导入到RAG...")
    print(f"{'='*80}\n")
    
    imported = 0
    total_chunks = 0
    
    for i, template in enumerate(templates):
        try:
            # 合并内容
            full_content = f"""
{template.get('template_name', 'Untitled')}

Industry: {template.get('industry', 'General')}
Stage: {template.get('stage', 'All Stages')}

=== BUSINESS PLAN TEMPLATE ===
{template.get('content', '')}

=== TIPS FOR WRITING ===
{template.get('tips', '')}
"""
            
            # 创建文档
            doc = AIDocument.objects.create(
                title=template.get('template_name', 'Untitled'),
                content=full_content,
                source_url='',
                doc_type='other',
                metadata={
                    'industry': template.get('industry', ''),
                    'stage': template.get('stage', ''),
                    'source': template.get('source', ''),
                    'tags': template.get('tags', []),
                    'data_type': 'business_plan_template',
                    'import_source': 'bp_full'
                }
            )
            
            # 分块
            chunks = rag_engine.text_splitter.split_text(full_content)
            
            for j, chunk_text in enumerate(chunks):
                chunk = AIChunk.objects.create(
                    document=doc,
                    content=chunk_text,
                    chunk_index=j,
                    chunk_metadata={'word_count': len(chunk_text), 'source': 'bp_full'}
                )
                
                embedding = rag_engine.embeddings.embed_query(chunk_text)
                AIEmbedding.objects.create(
                    chunk=chunk,
                    embedding_vector=embedding,
                    embedding_model='nomic-embed-text'
                )
            
            imported += 1
            total_chunks += len(chunks)
            print(f"  ✅ [{i+1}/{len(templates)}] {template['template_name'][:50]}... ({len(chunks)} chunks)")
            
        except Exception as e:
            print(f"  ❌ [{i+1}/{len(templates)}] 失败: {e}")
    
    print(f"\n✅ 成功导入 {imported}/{len(templates)} 个BP模板")
    print(f"   总Chunks: {total_chunks}")
    
    # 验证完整性
    from django.db.models import Q
    bp_docs = AIDocument.objects.filter(Q(metadata__import_source='bp_full'))
    bp_chunks = AIChunk.objects.filter(chunk_metadata__source='bp_full').count()
    bp_embeddings = AIEmbedding.objects.filter(chunk__chunk_metadata__source='bp_full').count()
    
    print(f"\n数据完整性验证:")
    print(f"  BP文档: {bp_docs.count()}")
    print(f"  BP Chunks: {bp_chunks}")
    print(f"  BP Embeddings: {bp_embeddings}")
    print(f"  完整性: {'✅ 通过' if bp_chunks == bp_embeddings else '❌ 失败'}")
    
    print(f"\n{'='*80}")
    print("✅ BP模板已成功导入RAG系统！")
    print("=" * 80)


if __name__ == '__main__':
    import_bp_templates()







