# backend/scripts/import_rag_documents.py
"""
智能导入RAG文档脚本
支持增量导入、失败重试、进度追踪
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Django 环境配置
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

import django
django.setup()

from django.db import transaction
from apps.ai.models import AIDocument, AIChunk, AIEmbedding
from apps.ai.services.rag_engine import RAGEngine
from apps.ai.services.document_processor import DocumentProcessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RAGDocumentImporter:
    """RAG文档智能导入器"""
    
    def __init__(self):
        self.rag_engine = RAGEngine()
        self.doc_processor = DocumentProcessor()
        
        # 目录路径
        self.base_dir = project_root / "data" / "rag_documents"
        self.pending_dir = self.base_dir / "pending"
        self.processed_dir = self.base_dir / "processed"
        self.failed_dir = self.base_dir / "failed"
        
        # 确保目录存在
        for dir_path in [self.pending_dir, self.processed_dir, self.failed_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def get_pending_files(self):
        """获取待处理的PDF文件"""
        return list(self.pending_dir.glob("*.pdf"))
    
    def is_already_imported(self, filename: str) -> bool:
        """检查文件是否已导入"""
        return AIDocument.objects.filter(title=filename).exists()
    
    def import_single_document(self, pdf_path: Path) -> bool:
        """
        导入单个PDF文档
        
        Returns:
            True if successful, False otherwise
        """
        filename = pdf_path.name
        logger.info(f"开始处理: {filename}")
        
        try:
            # 1. 检查是否已导入
            if self.is_already_imported(filename):
                logger.warning(f"文档已存在，跳过: {filename}")
                return True
            
            # 2. 提取PDF文本
            logger.info(f"  → 提取PDF文本...")
            text_content = self.doc_processor.extract_pdf_text(str(pdf_path))
            
            if not text_content or len(text_content.strip()) < 100:
                raise ValueError(f"PDF内容太短或为空: {len(text_content)} 字符")
            
            logger.info(f"  → 提取成功: {len(text_content)} 字符")
            
            # 3. 文本分块
            logger.info(f"  → 开始文本分块...")
            chunks = self.rag_engine.text_splitter.split_text(text_content)
            logger.info(f"  → 分块完成: {len(chunks)} 个块")
            
            # 4. 生成向量
            logger.info(f"  → 生成向量...")
            embeddings = self.rag_engine.embeddings.embed_documents(chunks)
            logger.info(f"  → 向量生成完成: {len(embeddings)} 个")
            
            # 5. 批量保存到数据库（使用事务）
            logger.info(f"  → 保存到数据库...")
            with transaction.atomic():
                # 5.1 创建文档记录
                doc = AIDocument.objects.create(
                    title=filename,
                    content=text_content[:1000],  # 只存储前1000字符作为预览
                    doc_type="course",  # 根据需要调整
                    metadata={
                        "file_path": str(pdf_path),
                        "file_size": pdf_path.stat().st_size,
                        "imported_at": datetime.now().isoformat(),
                    }
                )
                
                # 5.2 批量创建chunk和embedding
                chunk_objs = []
                for i, chunk_text in enumerate(chunks):
                    chunk_obj = AIChunk(
                        document=doc,
                        content=chunk_text,
                        chunk_index=i,
                        chunk_metadata={"length": len(chunk_text)}
                    )
                    chunk_objs.append(chunk_obj)
                
                # 批量插入chunks
                AIChunk.objects.bulk_create(chunk_objs)
                
                # 批量插入embeddings
                embedding_objs = []
                for chunk_obj, embedding_vector in zip(chunk_objs, embeddings):
                    # 重新获取chunk的ID（bulk_create后才有）
                    chunk_obj.refresh_from_db()
                    
                    embedding_obj = AIEmbedding(
                        chunk=chunk_obj,
                        embedding_vector=embedding_vector
                    )
                    embedding_objs.append(embedding_obj)
                
                AIEmbedding.objects.bulk_create(embedding_objs)
            
            logger.info(f"✅ 成功导入: {filename}")
            
            # 6. 移动到processed目录
            processed_path = self.processed_dir / filename
            pdf_path.rename(processed_path)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 导入失败: {filename}")
            logger.error(f"   错误详情: {str(e)}", exc_info=True)
            
            # 移动到failed目录
            failed_path = self.failed_dir / filename
            pdf_path.rename(failed_path)
            
            return False
    
    def import_all(self):
        """批量导入所有待处理文档"""
        pending_files = self.get_pending_files()
        
        if not pending_files:
            logger.info("没有待处理的PDF文件")
            return
        
        logger.info(f"发现 {len(pending_files)} 个待处理文件")
        
        success_count = 0
        failed_count = 0
        
        for pdf_path in pending_files:
            if self.import_single_document(pdf_path):
                success_count += 1
            else:
                failed_count += 1
        
        logger.info("=" * 60)
        logger.info(f"导入完成:")
        logger.info(f"  ✅ 成功: {success_count}")
        logger.info(f"  ❌ 失败: {failed_count}")
        logger.info(f"  📊 总计: {len(pending_files)}")
        logger.info("=" * 60)


def main():
    """主函数"""
    importer = RAGDocumentImporter()
    importer.import_all()


if __name__ == "__main__":
    main()