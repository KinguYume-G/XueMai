"""
RAG检索Step - 从向量数据库检索相关文档
"""

from typing import Dict, Any
import logging

from .base_step import BaseStep, StepResult, ExecutionContext

logger = logging.getLogger(__name__)


class RAGRetrieveStep(BaseStep):
    """RAG文档检索步骤"""
    
    def execute(self, context: ExecutionContext) -> StepResult:
        """
        执行RAG检索
        
        Config参数:
            query: 检索查询（支持模板变量）
            top_k: 返回文档数量（默认5）
            min_similarity: 最小相似度阈值（默认0.7）
        """
        try:
            # 获取配置
            query_template = self.config.get('query', context.initial_input)
            top_k = self.config.get('top_k', 5)
            min_similarity = self.config.get('min_similarity', 0.7)
            
            # 解析查询模板
            query = self._resolve_variable(query_template, context)
            
            logger.info(f"[RAG检索Step] 查询: {query}, top_k={top_k}")
            
            # 执行RAG检索
            from apps.ai.services.rag_engine import RAGEngine
            rag_engine = RAGEngine()
            
            docs = rag_engine.retrieve(query=query, top_k=top_k)
            
            # 过滤低相似度文档
            filtered_docs = [
                doc for doc in docs 
                if doc.metadata.get('similarity', 0) >= min_similarity
            ]
            
            # 格式化结果
            doc_list = []
            for i, doc in enumerate(filtered_docs, 1):
                doc_list.append({
                    'index': i,
                    'content': doc.page_content,
                    'source': doc.metadata.get('title', '未知来源'),
                    'similarity': doc.metadata.get('similarity', 0),
                })
            
            # 生成合并的上下文文本
            context_text = "\n\n".join([
                f"【参考资料 {d['index']}】\n来源：{d['source']}\n内容：{d['content']}"
                for d in doc_list
            ])
            
            logger.info(f"[RAG检索Step] 检索到 {len(filtered_docs)} 个高质量文档")
            
            return StepResult(
                success=True,
                data={
                    'docs': doc_list,
                    'context': context_text,
                    'total_count': len(filtered_docs),
                },
                metadata={
                    'query': query,
                    'top_k': top_k,
                    'min_similarity': min_similarity,
                }
            )
            
        except Exception as e:
            logger.error(f"[RAG检索Step] 执行失败: {e}", exc_info=True)
            return StepResult(
                success=False,
                error=f"RAG检索失败: {str(e)}"
            )
