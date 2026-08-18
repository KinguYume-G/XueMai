"""
快速导入公司信息到RAG系统（简化版）
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

# 加载数据
file_path = Path(__file__).parent.parent / 'backend' / 'data' / 'crawled' / 'company_test.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

companies = data.get('companies', [])
print(f"导入 {len(companies)} 家公司...")

rag_engine = RAGEngine()
imported, total_chunks = 0, 0

for company in companies:
    content = f"{company['company_name']}\n{company['industry']}\n{company['size']}\n{company['location']}\n\n{company.get('description', '')}"
    doc = AIDocument.objects.create(
        title=company['company_name'],
        content=content,
        source_url=company.get('website', ''),
        doc_type='other',
        metadata={'industry': company['industry'], 'size': company['size'], 'data_type': 'company_info', 'import_source': 'company_full'}
    )
    chunks = rag_engine.text_splitter.split_text(content)
    for j, chunk_text in enumerate(chunks):
        chunk = AIChunk.objects.create(document=doc, content=chunk_text, chunk_index=j, chunk_metadata={'source': 'company_full'})
        embedding = rag_engine.embeddings.embed_query(chunk_text)
        AIEmbedding.objects.create(chunk=chunk, embedding_vector=embedding, embedding_model='nomic-embed-text')
    imported += 1
    total_chunks += len(chunks)
    print(f"  ✅ {company['company_name']} ({len(chunks)} chunks)")

print(f"\n✅ 成功导入 {imported}/{len(companies)} 家公司，总 {total_chunks} chunks")







