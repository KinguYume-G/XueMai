"""导入扩展的BP模板（12个）"""
import sys, os, django, json
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root)); sys.path.insert(0, str(project_root / 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings'); django.setup()

from apps.ai.services.rag_engine import RAGEngine
from apps.ai.models import AIDocument, AIChunk, AIEmbedding

print("="*80); print("📄 导入扩展的BP模板（12个）- 指令6-5"); print("="*80)

# 加载数据
file_path = Path(__file__).parent.parent / 'backend' / 'data' / 'crawled' / 'bp_full_expanded.json'
with open(file_path, 'r', encoding='utf-8') as f:
    templates = json.load(f).get('templates', [])
print(f"\n✅ 加载了 {len(templates)} 个BP模板")

# 清理旧数据
print(f"\n清理旧BP数据...")
old_docs = AIDocument.objects.filter(metadata__import_source='bp_full')
old_count = old_docs.count()
if old_count > 0:
    for doc in old_docs:
        AIEmbedding.objects.filter(chunk__document=doc).delete()
        AIChunk.objects.filter(document=doc).delete()
    old_docs.delete()
    print(f"  ✅ 已删除 {old_count} 个旧文档")

# 导入
rag = RAGEngine(); imported, total_chunks = 0, 0
print(f"\n开始导入...\n")

for i, t in enumerate(templates):
    content = f"{t['template_name']}\n{t['industry']}\n{t['stage']}\n\n{t['content']}\n\n{t['tips']}"
    doc = AIDocument.objects.create(title=t['template_name'], content=content, source_url='', doc_type='other', metadata={'industry': t['industry'], 'stage': t['stage'], 'data_type': 'business_plan', 'import_source': 'bp_full'})
    chunks = rag.text_splitter.split_text(content)
    for j, ct in enumerate(chunks):
        chunk = AIChunk.objects.create(document=doc, content=ct, chunk_index=j, chunk_metadata={'source': 'bp_full'})
        AIEmbedding.objects.create(chunk=chunk, embedding_vector=rag.embeddings.embed_query(ct), embedding_model='nomic-embed-text')
    imported += 1; total_chunks += len(chunks)
    print(f"  ✅ [{i+1}/{len(templates)}] {t['template_name'][:50]}... ({len(chunks)} chunks)")

print(f"\n✅ 成功导入 {imported} 个BP模板，总 {total_chunks} chunks")

# 验证
from django.db.models import Q
bp_docs = AIDocument.objects.filter(Q(metadata__import_source='bp_full')).count()
bp_chunks = AIChunk.objects.filter(Q(chunk_metadata__source='bp_full')).count()
bp_embeddings = AIEmbedding.objects.filter(Q(chunk__chunk_metadata__source='bp_full')).count()
print(f"\n数据完整性: BP文档={bp_docs}, Chunks={bp_chunks}, Embeddings={bp_embeddings}")
print(f"✅ {'通过' if bp_chunks == bp_embeddings else '失败'}")
print("="*80)







