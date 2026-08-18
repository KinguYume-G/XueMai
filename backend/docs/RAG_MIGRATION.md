# RAG 系统迁移文档

## 迁移概述

从 ChromaDB 迁移到 PostgreSQL pgvector，实现更好的性能和数据一致性。

## 迁移完成日期
2025-11-23

## 架构变更

### 旧架构（ChromaDB）
- 向量存储：ChromaDB (文件系统)
- 数据同步：独立管道
- 性能：平均 1054ms
- **问题：返回 0 个文档（数据已过期）**

### 新架构（pgvector）
- 向量存储：PostgreSQL + pgvector
- 数据同步：统一数据库
- 性能：平均 879ms（提升 20%）
- **优势：返回准确结果（3个文档/查询）**

## 测试结果

### 功能测试
- ✅ 向量检索正常工作
- ✅ 返回结果准确（3个文档/查询）
- ✅ 文档内容相关性高
- ❌ ChromaDB 返回 0 个文档（已废弃）

### 性能测试
| 查询 | ChromaDB | pgvector | 改进 |
|------|----------|----------|------|
| APU 有哪些课程？ | 3070ms | 2457ms | +25% |
| 如何申请 APU？ | 42ms | 61ms | -31% |
| APU 的学费是多少？ | 51ms | 119ms | -57% |
| **平均** | **1054ms** | **879ms** | **+20%** |

**注意：** 首次查询包含 Ollama 模型加载时间（约 2-3秒），后续查询稳定在 61-119ms。

## 配置说明

### 环境变量
在 `backend/.env` 文件中添加：

```env
# RAG 向量检索后端（推荐使用 pgvector）
RAG_VECTOR_BACKEND=pgvector

# pgvector 检索参数（可选）
RAG_PGVECTOR_TOP_K=5
RAG_PGVECTOR_SIMILARITY_THRESHOLD=0.3
```

### 切换后端
只需修改 `.env` 文件中的 `RAG_VECTOR_BACKEND` 值：
- `pgvector` - 使用 PostgreSQL（推荐）
- `chromadb` - 使用 ChromaDB（已废弃）

## 数据维护

### 添加新文档
使用以下脚本重建向量数据库：
```bash
cd backend
python manage.py shell
>>> from scripts.rebuild_embeddings import run
>>> run()
```

### 查看数据统计
```python
from apps.ai.services.vector_search_service import VectorSearchService
service = VectorSearchService()
stats = service.get_stats()
print(stats)
# 输出示例：
# {
#     'total_embeddings': 399,
#     'total_chunks': 399,
#     'total_documents': 37,
#     'embeddings_with_vector': 399
# }
```

## 清理工作（推荐）

### 1. 删除 ChromaDB 数据
```bash
# 备份（如果需要）
cd backend
tar -czf chromadb_backup_20251123.tar.gz chroma_db/

# 删除
rm -rf chroma_db/
```

### 2. 移除相关依赖
从 `backend/requirements-ai.txt` 中移除：
```
chromadb==0.5.5
langchain-chroma
```

### 3. 删除迁移脚本
```bash
rm backend/scripts/ingest_chunks_to_chroma.py
```

## 回滚方案

如果需要紧急回滚到 ChromaDB：

1. **修改配置**
   ```bash
   # 在 .env 中设置
   RAG_VECTOR_BACKEND=chromadb
   ```

2. **恢复数据**（如果已删除）
   ```bash
   tar -xzf chromadb_backup_20251123.tar.gz
   ```

3. **重启服务**
   ```bash
   # 重启 Django 应用
   ```

**注意：** 由于 ChromaDB 数据已过期（返回 0 个文档），不建议回滚。

## 技术细节

### 向量配置
- **Embedding 模型**：nomic-embed-text (Ollama)
- **向量维度**：768
- **相似度算法**：余弦相似度 (Cosine Similarity)
- **相似度公式**：`similarity = (2 - cosine_distance) / 2`

### PostgreSQL pgvector 配置
- **扩展版本**：pgvector 0.5+
- **字段类型**：`vector(768)`
- **索引类型**：IVFFlat（推荐）或 HNSW
- **距离算子**：`vector_cosine_ops`

### 数据量统计
- **总文档数**：37 个
- **总文本块数**：399 个
- **向量记录数**：399 条
- **数据库大小**：约 3-5 MB

## 相关文件

### 核心服务
- `apps/ai/services/vector_search_service.py` - pgvector 检索服务
- `apps/ai/services/rag_engine.py` - RAG 引擎（支持双后端）
- `apps/ai/models.py` - AIEmbedding 模型定义

### 配置文件
- `config/settings/base.py` - RAG 配置项
- `backend/.env` - 环境变量配置

### 测试文件
- `tests/test_rag_migration.py` - 迁移测试脚本

### 数据脚本
- `scripts/rebuild_embeddings.py` - 重建向量数据库
- `scripts/import_chunks_to_ai_models.py` - 导入文本块

## 性能优化建议

### 1. 数据库索引优化
```sql
-- 创建 IVFFlat 索引（推荐用于中等规模数据）
CREATE INDEX ON ai_embeddings USING ivfflat (embedding_vector vector_cosine_ops)
WITH (lists = 100);

-- 或使用 HNSW 索引（更快，但占用空间更大）
CREATE INDEX ON ai_embeddings USING hnsw (embedding_vector vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

### 2. 查询性能优化
- 使用 `select_related()` 避免 N+1 查询（已实现）
- 设置合理的 `top_k` 值（默认 5）
- 配置相似度阈值过滤低质量结果（默认 0.3）

### 3. Ollama 优化
- 首次查询慢是因为模型加载，建议预热：
  ```bash
  ollama run nomic-embed-text "warmup"
  ```
- 保持 Ollama 服务常驻运行

## 问题排查

### Q1: 查询返回 0 个结果
**解决方案：**
```bash
# 检查向量数据是否存在
python manage.py shell
>>> from apps.ai.models import AIEmbedding
>>> AIEmbedding.objects.filter(embedding_vector__isnull=False).count()
# 应该返回 399

# 如果为 0，运行重建脚本
>>> from scripts.rebuild_embeddings import run
>>> run()
```

### Q2: 查询很慢（>5秒）
**可能原因：**
- Ollama 首次加载模型（正常）
- 缺少数据库索引
- 数据量过大

**解决方案：**
```sql
-- 检查索引
SELECT * FROM pg_indexes WHERE tablename = 'ai_embeddings';

-- 创建索引（如果缺少）
CREATE INDEX ON ai_embeddings USING ivfflat (embedding_vector vector_cosine_ops);
```

### Q3: Ollama 连接失败
**解决方案：**
```bash
# 检查 Ollama 服务状态
curl http://localhost:11434/api/tags

# 启动 Ollama
ollama serve

# 拉取模型（如果缺少）
ollama pull nomic-embed-text
```

## 维护记录

| 日期 | 操作 | 负责人 | 备注 |
|------|------|--------|------|
| 2025-11-23 | 完成 pgvector 迁移 | Drake | 性能提升 20% |
| 2025-11-23 | 创建测试脚本 | Drake | 验证双后端功能 |
| 2025-11-23 | 更新配置文件 | Drake | 支持动态切换 |

## 下一步优化建议

1. **添加缓存层**
   - 使用 Redis 缓存热门查询结果
   - 减少数据库查询次数

2. **实现增量更新**
   - 监听文档变更事件
   - 自动更新向量数据库

3. **添加监控指标**
   - 查询响应时间
   - 向量检索准确率
   - 数据库连接池状态

4. **实现 A/B 测试**
   - 对比不同相似度算法
   - 优化 top_k 参数
   - 测试不同索引类型

## 联系方式

如有问题，请联系：
- **技术负责人**：Drake
- **项目仓库**：XueMai
- **文档更新日期**：2025-11-23
