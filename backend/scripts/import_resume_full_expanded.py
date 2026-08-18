"""
导入扩展的简历模板（35个）到RAG系统
严格执行指令5-5的完整流程
"""
import sys, os, django
from pathlib import Path
import json

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.ai.services.rag_engine import RAGEngine
from apps.ai.models import AIDocument, AIChunk, AIEmbedding

print("="*80)
print("📄 导入扩展的简历模板（35个）- 指令5-5")
print("="*80)

# 1. 加载扩展后的简历数据
file_path = Path(__file__).parent.parent / 'backend' / 'data' / 'crawled' / 'resume_full.json'
print(f"\n加载数据: {file_path}")

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

resumes = data.get('resumes', [])
print(f"✅ 加载了 {len(resumes)} 个简历模板")

# 2. 初始化RAG引擎
rag_engine = RAGEngine()

# 3. 删除旧的测试数据（resume_test）
print(f"\n清理旧的测试数据...")
old_docs = AIDocument.objects.filter(metadata__import_source='resume_test')
old_count = old_docs.count()
if old_count > 0:
    # 删除相关的embeddings和chunks
    for doc in old_docs:
        AIEmbedding.objects.filter(chunk__document=doc).delete()
        AIChunk.objects.filter(document=doc).delete()
    old_docs.delete()
    print(f"  ✅ 已删除 {old_count} 个旧的测试文档")
else:
    print(f"  ℹ️  没有旧数据需要清理")

# 4. 导入新的完整简历模板
print(f"\n{'='*80}")
print(f"开始导入 {len(resumes)} 个简历模板...")
print(f"{'='*80}\n")

imported, total_chunks = 0, 0

for i, resume in enumerate(resumes):
    try:
        # 合并content和tips作为完整内容
        full_content = f"""
{resume.get('template_name', 'Untitled')}

Industry: {resume.get('industry', 'General')}
Level: {resume.get('level', 'All Levels')}
Experience: {resume.get('years_experience', 'Any')}

=== RESUME TEMPLATE ===
{resume.get('content', '')}

=== USAGE TIPS ===
{resume.get('tips', '')}
"""
        
        # 创建AIDocument
        doc = AIDocument.objects.create(
            title=resume.get('template_name', 'Untitled'),
            content=full_content,
            source_url='',
            doc_type='other',
            metadata={
                'industry': resume.get('industry', ''),
                'level': resume.get('level', ''),
                'years_experience': resume.get('years_experience', ''),
                'source': resume.get('source', ''),
                'tags': resume.get('tags', []),
                'category': resume.get('category', 'resume'),
                'subcategory': resume.get('subcategory', 'template'),
                'data_type': 'resume_template',
                'import_source': 'resume_full'
            }
        )
        
        # 使用RAG引擎分块
        chunks = rag_engine.text_splitter.split_text(full_content)
        
        for j, chunk_text in enumerate(chunks):
            # 创建chunk
            chunk = AIChunk.objects.create(
                document=doc,
                content=chunk_text,
                chunk_index=j,
                chunk_metadata={
                    'word_count': len(chunk_text),
                    'source': 'resume_full'
                }
            )
            
            # 生成embedding
            embedding_vector = rag_engine.embeddings.embed_query(chunk_text)
            
            AIEmbedding.objects.create(
                chunk=chunk,
                embedding_vector=embedding_vector,
                embedding_model='nomic-embed-text'
            )
        
        imported += 1
        total_chunks += len(chunks)
        print(f"  ✅ [{i+1}/{len(resumes)}] {resume['template_name'][:50]}... ({len(chunks)} chunks)")
        
    except Exception as e:
        print(f"  ❌ [{i+1}/{len(resumes)}] 导入失败: {e}")

print(f"\n✅ 成功导入 {imported}/{len(resumes)} 个简历模板")
print(f"   总Chunks: {total_chunks}")

# 5. 验证完整性
from django.db.models import Q
resume_docs = AIDocument.objects.filter(Q(metadata__import_source='resume_full'))
resume_chunks = AIChunk.objects.filter(chunk_metadata__source='resume_full').count()
resume_embeddings = AIEmbedding.objects.filter(chunk__chunk_metadata__source='resume_full').count()

print(f"\n数据完整性验证:")
print(f"  简历文档: {resume_docs.count()}")
print(f"  简历Chunks: {resume_chunks}")
print(f"  简历Embeddings: {resume_embeddings}")
print(f"  完整性: {'✅ 通过' if resume_chunks == resume_embeddings else '❌ 失败'}")

print(f"\n{'='*80}")
print("✅ 简历模板已成功导入RAG系统！")
print("="*80)







