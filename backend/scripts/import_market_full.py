"""快速导入市场报告到RAG"""
import sys, os, django, json
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root)); sys.path.insert(0, str(project_root / 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings'); django.setup()
from apps.ai.services.rag_engine import RAGEngine
from apps.ai.models import AIDocument, AIChunk, AIEmbedding

file_path = Path(__file__).parent.parent / 'backend' / 'data' / 'crawled' / 'market_test.json'
with open(file_path, 'r', encoding='utf-8') as f:
    reports = json.load(f).get('reports', [])

print(f"导入 {len(reports)} 篇报告..."); rag = RAGEngine(); imported, total_chunks = 0, 0
for r in reports:
    doc = AIDocument.objects.create(title=r['title'], content=r['content'], source_url='', doc_type='other', metadata={'category': r['category'], 'data_type': 'market_report', 'import_source': 'market_full'})
    chunks = rag.text_splitter.split_text(r['content'])
    for j, ct in enumerate(chunks):
        chunk = AIChunk.objects.create(document=doc, content=ct, chunk_index=j, chunk_metadata={'source': 'market_full'})
        AIEmbedding.objects.create(chunk=chunk, embedding_vector=rag.embeddings.embed_query(ct), embedding_model='nomic-embed-text')
    imported += 1; total_chunks += len(chunks)
    print(f"  ✅ {r['title'][:50]}... ({len(chunks)} chunks)")
print(f"\n✅ 导入 {imported} 篇报告，{total_chunks} chunks")







