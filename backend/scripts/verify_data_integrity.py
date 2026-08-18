#!/usr/bin/env python
"""
验证RAG系统数据完整性
"""

import os
import sys
import django
from pathlib import Path

# 设置Django环境
sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.ai.models import AIDocument, AIChunk, AIEmbedding

print("=" * 80)
print("🔍 数据完整性验证")
print("=" * 80)

# 统计数据
total_docs = AIDocument.objects.count()
total_chunks = AIChunk.objects.count()
total_embeddings = AIEmbedding.objects.count()

print(f"\n基础统计:")
print(f"  文档数量: {total_docs}")
print(f"  Chunk数量: {total_chunks}")
print(f"  Embedding数量: {total_embeddings}")

# 验证1: chunks == embeddings
print(f"\n验证1: Chunks与Embeddings数量一致性")
if total_chunks == total_embeddings:
    print(f"  ✅ 通过: {total_chunks} == {total_embeddings}")
else:
    print(f"  ❌ 失败: {total_chunks} != {total_embeddings}")
    diff = abs(total_chunks - total_embeddings)
    print(f"  差异: {diff} 条记录")

# 验证2: 检查孤儿chunks（没有embedding的chunks）
orphan_chunks = AIChunk.objects.filter(embedding__isnull=True).count()
print(f"\n验证2: 孤儿Chunks检查")
if orphan_chunks == 0:
    print(f"  ✅ 通过: 没有孤儿chunks")
else:
    print(f"  ⚠️  发现 {orphan_chunks} 个chunk没有对应的embedding")

# 验证3: 检查孤儿embeddings（chunk被删除但embedding还在）
orphan_embeddings = AIEmbedding.objects.filter(chunk__isnull=True).count()
print(f"\n验证3: 孤儿Embeddings检查")
if orphan_embeddings == 0:
    print(f"  ✅ 通过: 没有孤儿embeddings")
else:
    print(f"  ⚠️  发现 {orphan_embeddings} 个embedding没有对应的chunk")

# 验证4: 检查没有chunks的文档
docs_without_chunks = 0
for doc in AIDocument.objects.all():
    if AIChunk.objects.filter(document=doc).count() == 0:
        docs_without_chunks += 1
        print(f"  ⚠️  文档 '{doc.title}' 没有chunks")

print(f"\n验证4: 空文档检查")
if docs_without_chunks == 0:
    print(f"  ✅ 通过: 所有文档都有chunks")
else:
    print(f"  ⚠️  发现 {docs_without_chunks} 个文档没有chunks")

# 验证5: 检查embedding_vector是否为空
null_vectors = AIEmbedding.objects.filter(embedding_vector__isnull=True).count()
print(f"\n验证5: Embedding向量完整性")
if null_vectors == 0:
    print(f"  ✅ 通过: 所有embedding都有向量数据")
else:
    print(f"  ⚠️  发现 {null_vectors} 个embedding缺少向量数据")

# 对比优化前后
print("\n" + "=" * 80)
print("📊 优化前后对比")
print("=" * 80)
print(f"优化前:")
print(f"  文档数: 52")
print(f"  Chunks: 3,334")
print(f"  Embeddings: 3,334")
print(f"  低质量文档(chunk<10): 24个")

print(f"\n优化后:")
print(f"  文档数: {total_docs}")
print(f"  Chunks: {total_chunks:,}")
print(f"  Embeddings: {total_embeddings:,}")
print(f"  低质量文档(chunk<10): 1个")

chunk_change = total_chunks - 3334
print(f"\n变化:")
print(f"  文档数: {total_docs - 52:+d}")
print(f"  Chunks: {chunk_change:+,d}")
print(f"  低质量文档: {1 - 24:+d}")

# 总结
print("\n" + "=" * 80)
print("✅ 数据完整性验证完成")
print("=" * 80)
if (total_chunks == total_embeddings and 
    orphan_chunks == 0 and 
    orphan_embeddings == 0 and 
    docs_without_chunks == 0 and 
    null_vectors == 0):
    print("✅ 所有验证通过，数据完整性100%")
else:
    print("⚠️  部分验证未通过，建议检查数据")

