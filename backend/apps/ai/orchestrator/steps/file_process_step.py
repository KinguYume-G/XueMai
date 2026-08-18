"""
文件处理Step - 处理用户上传的文件
"""

from typing import Dict, Any
import logging

from .base_step import BaseStep, StepResult, ExecutionContext

logger = logging.getLogger(__name__)


class FileProcessStep(BaseStep):
    """文件处理步骤"""
    
    def execute(self, context: ExecutionContext) -> StepResult:
        """
        执行文件处理
        
        Config参数:
            file_source: 文件来源 ('user_upload' | 'step_output')
            process_type: 处理类型 ('extract_text' | 'analyze' | 'summarize')
            file_index: 文件索引（默认0，第一个文件）
        """
        try:
            file_source = self.config.get('file_source', 'user_upload')
            process_type = self.config.get('process_type', 'extract_text')
            file_index = self.config.get('file_index', 0)
            
            logger.info(f"[文件处理Step] 来源: {file_source}, 类型: {process_type}")
            
            # 获取文件
            if file_source == 'user_upload':
                if not context.uploaded_files:
                    return StepResult(
                        success=False,
                        error="没有上传的文件"
                    )
                
                if file_index >= len(context.uploaded_files):
                    return StepResult(
                        success=False,
                        error=f"文件索引 {file_index} 超出范围（共{len(context.uploaded_files)}个文件）"
                    )
                
                document = context.uploaded_files[file_index]
                
                # 提取文本
                if process_type == 'extract_text':
                    extracted_text = document.content
                    
                    if not extracted_text:
                        return StepResult(
                            success=False,
                            error="文件内容为空，可能是处理失败"
                        )
                    
                    logger.info(f"[文件处理Step] 提取文本长度: {len(extracted_text)}")
                    
                    # Get file extension from metadata if available
                    file_extension = document.metadata.get('file_extension', 'unknown')
                    
                    return StepResult(
                        success=True,
                        data={
                            'extracted_text': extracted_text,
                            'file_title': document.title,
                            'file_extension': file_extension,
                            'text_length': len(extracted_text),
                        },
                        metadata={
                            'file_id': document.id,
                            'process_type': process_type,
                        }
                    )
            else:
                return StepResult(
                    success=False,
                    error=f"不支持的文件来源: {file_source}"
                )
            
        except Exception as e:
            logger.error(f"[文件处理Step] 执行失败: {e}", exc_info=True)
            return StepResult(
                success=False,
                error=f"文件处理失败: {str(e)}"
            )
