"""
Retrieval-Augmented Generation (RAG) engine utilities.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from django.conf import settings
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


class RAGEngine:
    """Manage document ingestion, retrieval, and response generation."""

    def __init__(self) -> None:
        """
        初始化 RAG 引擎

        使用 PostgreSQL pgvector 扩展作为向量检索后端
        """
        try:
            logger.info(f"初始化 RAGEngine，向量后端: {settings.RAG_VECTOR_BACKEND}")

            # 1. 初始化 Ollama Embeddings
            self.embeddings = OllamaEmbeddings(
                model=settings.EMBEDDING_MODEL,
                base_url=settings.OLLAMA_BASE_URL,
            )

            # 2. 初始化 pgvector 后端
            from .vector_search_service import VectorSearchService

            self.vector_search = VectorSearchService()
            logger.info("RAG 后端：PostgreSQL pgvector")

            # 3. 初始化文本分割器
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=100,
                length_function=len,
                separators=["\n\n", "\n", " ", ""],
            )

            logger.info("RAG 引擎初始化完成")

        except Exception as exc:
            logger.error(f"RAG 引擎初始化失败: {exc}", exc_info=True)
            raise

    def ingest_document(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        将新文档添加到向量库

        pgvector 模式下，需要通过 Django 模型手动添加

        Args:
            file_path: UTF-8 文本文档路径
            metadata: 可选的元数据字典

        Returns:
            添加的文本块数量
        """
        logger.warning(
            "pgvector 模式不支持动态添加文档，"
            "请使用 Django 管理后台或 rebuild_embeddings.py 脚本"
        )
        return 0

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """
        根据查询问题检索相关文档

        使用 PostgreSQL pgvector 检索后端

        Args:
            query: 用户查询问题
            top_k: 返回文档数量
            filters: 可选的元数据过滤条件

        Returns:
            Document 对象列表，包含检索到的文档内容和元数据
        """
        logger.info(f"检索查询: {query[:50]}... (top_k={top_k})")

        try:
            # Global RAG must never search disabled records. User uploads are
            # injected explicitly by the authenticated API after an ownership
            # check and are intentionally excluded from the shared index.
            safe_filters = dict(filters or {})
            safe_filters["is_active"] = True
            safe_filters["system_documents_only"] = True
            return self._retrieve_from_pgvector(query, top_k, safe_filters)

        except Exception as exc:
            logger.error(f"文档检索失败: {exc}", exc_info=True)
            return []

    def _retrieve_from_pgvector(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """
        使用 PostgreSQL pgvector 检索相关文档（新版方法）

        Args:
            query: 用户查询问题
            top_k: 返回文档数量
            filters: 可选的过滤条件

        Returns:
            Document 对象列表，格式与 ChromaDB 一致
        """
        if not self.vector_search:
            logger.error("VectorSearchService 未初始化")
            return []

        try:
            # 1. 生成查询向量
            query_vector = self.embeddings.embed_query(query)

            # 2. 使用 pgvector 检索
            results = self.vector_search.search_similar(
                query_vector=query_vector,
                top_k=top_k,
                filters=filters,
            )

            # 3. 转换为 LangChain Document 格式
            docs = []
            for result in results:
                # 将相似度添加到 metadata 中
                metadata = result["metadata"].copy()
                metadata["similarity"] = result["similarity"]

                doc = Document(page_content=result["page_content"], metadata=metadata)
                docs.append(doc)

            # 4. 使用配置的余弦相似度阈值过滤低质量结果
            original_count = len(docs)
            threshold = settings.RAG_PGVECTOR_SIMILARITY_THRESHOLD
            filtered_docs = [
                doc for doc in docs if doc.metadata.get("similarity", -1) >= threshold
            ]

            logger.info(
                f"pgvector 检索完成：原始结果={original_count}，"
                f"通过阈值（>={threshold}）={len(filtered_docs)}"
            )

            return filtered_docs

        except Exception as exc:
            logger.error(f"pgvector 检索失败: {exc}", exc_info=True)
            return []

    def rag_query(
        self,
        question: str,
        ollama_client: Any,
        top_k: int = 3,
    ) -> str:
        """
        Execute a complete RAG workflow for a user question.

        Args:
            question: User question to answer.
            ollama_client: Instance of `OllamaClient` used for generation.
            top_k: Number of documents to use as supporting context.

        Returns:
            The generated answer string.
        """
        try:
            docs = self.retrieve(question, top_k=top_k)
            context = "\n\n".join(doc.page_content for doc in docs)

            prompt_path = Path(__file__).parent.parent / "prompts" / "academic.txt"
            with open(prompt_path, "r", encoding="utf-8") as prompt_file:
                system_prompt = prompt_file.read()

            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        "Use the following context to answer the question.\n\n"
                        f"Context:\n{context}\n\n"
                        f"Question:\n{question}\n\n"
                        "Answer only with information grounded in the context."
                    ),
                },
            ]

            result = ollama_client.chat_completion(messages=messages)
            logger.info("RAG query completed")
            return result
        except Exception as exc:
            logger.error("Failed to execute RAG query: %s", exc)
            raise
