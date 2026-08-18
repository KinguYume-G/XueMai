"""
向量检索服务 - 基于 PostgreSQL pgvector 的向量相似度搜索

提供高性能的向量检索功能，替代 ChromaDB。
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.db.models import QuerySet
from pgvector.django import CosineDistance

from apps.ai.models import AIChunk, AIDocument, AIEmbedding

logger = logging.getLogger(__name__)


class VectorSearchService:
    """
    向量检索服务类

    封装基于 PostgreSQL pgvector 的向量相似度搜索逻辑。
    使用余弦距离（Cosine Distance）计算向量相似度。
    """

    def __init__(self) -> None:
        """初始化向量检索服务"""
        self.vector_dimension = settings.VECTOR_DIMENSION
        logger.info("初始化 VectorSearchService")

    def search_similar(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        根据查询向量检索最相似的文档块

        Args:
            query_vector: 查询向量（768 维浮点数列表）
            top_k: 返回结果数量，默认 5
            filters: 可选的过滤条件，例如 {'doc_type': 'course'}

        Returns:
            返回格式与 ChromaDB 的 similarity_search() 一致的结果列表:
            [
                {
                    'page_content': '文档内容',
                    'metadata': {
                        'chunk_id': 123,
                        'document_id': 45,
                        'doc_type': 'course',
                        'title': '文档标题',
                        'source': '来源',
                        'chunk_index': 0,
                        ...
                    },
                    'similarity': 0.95  # 相似度分数 (0-1)
                }
            ]

        Raises:
            ValueError: 当 query_vector 为空或维度不正确时
            Exception: 数据库查询错误
        """
        # 1. 参数验证
        if not query_vector:
            raise ValueError("查询向量不能为空")

        if len(query_vector) != self.vector_dimension:
            raise ValueError(
                f"查询向量维度必须为 {self.vector_dimension}，当前为 {len(query_vector)}"
            )

        if top_k < 1:
            raise ValueError(f"top_k 必须大于 0，当前为 {top_k}")

        start_time = time.time()

        try:
            # 2. 构建基础查询
            # 使用 select_related 优化性能，避免 N+1 查询
            queryset = AIEmbedding.objects.select_related("chunk", "chunk__document").filter(
                embedding_vector__isnull=False  # 只查询有向量的记录
            )

            # 3. 应用过滤条件
            if filters:
                queryset = self._apply_filters(queryset, filters)

            # 4. 计算余弦距离并排序
            # CosineDistance 返回距离值（0-2），距离越小越相似
            queryset = queryset.annotate(
                distance=CosineDistance("embedding_vector", query_vector)
            ).order_by("distance")[:top_k]

            # 5. 转换为统一格式
            results = []
            for embedding in queryset:
                chunk = embedding.chunk
                document = chunk.document

                # pgvector CosineDistance = 1 - cosine similarity.
                similarity = max(-1.0, min(1.0, 1.0 - embedding.distance))

                # 构建元数据
                metadata = {
                    "chunk_id": chunk.id,
                    "document_id": document.id,
                    "doc_type": document.doc_type,
                    "title": document.title,
                    "source": document.source_url or "",
                    "chunk_index": chunk.chunk_index,
                    "created_at": chunk.created_at.isoformat(),
                }

                # 合并 chunk 的自定义元数据
                if chunk.chunk_metadata:
                    metadata.update(chunk.chunk_metadata)

                # 合并 document 的自定义元数据
                if document.metadata:
                    for key, value in document.metadata.items():
                        if key not in metadata:
                            metadata[key] = value

                results.append(
                    {
                        "page_content": chunk.content,
                        "metadata": metadata,
                        "similarity": similarity,
                    }
                )

            # 6. 记录查询性能
            elapsed_ms = int((time.time() - start_time) * 1000)
            logger.info(
                f"向量检索完成: 查询向量维度={len(query_vector)}, "
                f"返回结果={len(results)}/{top_k}, "
                f"耗时={elapsed_ms}ms"
            )

            return results

        except Exception as exc:
            logger.error(f"向量检索失败: {exc}", exc_info=True)
            raise

    def _apply_filters(self, queryset: QuerySet, filters: Dict[str, Any]) -> QuerySet:
        """
        应用过滤条件到查询集

        Args:
            queryset: 原始查询集
            filters: 过滤条件字典

        Returns:
            应用过滤后的查询集
        """
        try:
            # 支持的过滤字段
            if "doc_type" in filters:
                queryset = queryset.filter(chunk__document__doc_type=filters["doc_type"])

            if "university_id" in filters:
                queryset = queryset.filter(chunk__document__university_id=filters["university_id"])

            if "is_active" in filters:
                queryset = queryset.filter(chunk__document__is_active=filters["is_active"])

            if filters.get("system_documents_only"):
                queryset = queryset.filter(chunk__document__uploaded_by__isnull=True)

            if "title_contains" in filters:
                queryset = queryset.filter(
                    chunk__document__title__icontains=filters["title_contains"]
                )

            logger.debug(f"应用过滤条件: {filters}")

        except Exception as exc:
            logger.warning(f"应用过滤条件时出错: {exc}，跳过部分过滤条件")

        return queryset

    def get_stats(self) -> Dict[str, int]:
        """
        获取向量数据库统计信息

        Returns:
            统计信息字典:
            {
                'total_embeddings': 总向量数,
                'total_chunks': 总文本块数,
                'total_documents': 总文档数,
                'embeddings_with_vector': 有向量的记录数
            }
        """
        try:
            stats = {
                "total_embeddings": AIEmbedding.objects.count(),
                "total_chunks": AIChunk.objects.count(),
                "total_documents": AIDocument.objects.count(),
                "embeddings_with_vector": AIEmbedding.objects.filter(
                    embedding_vector__isnull=False
                ).count(),
            }

            logger.info(f"向量数据库统计: {stats}")
            return stats

        except Exception as exc:
            logger.error(f"获取统计信息失败: {exc}", exc_info=True)
            raise
