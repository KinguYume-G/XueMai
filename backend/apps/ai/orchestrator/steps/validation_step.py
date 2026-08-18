"""
验证Step - 验证输出质量
"""

from typing import Dict, Any
import logging

from .base_step import BaseStep, StepResult, ExecutionContext

logger = logging.getLogger(__name__)


class ValidationStep(BaseStep):
    """输出验证步骤"""
    
    def execute(self, context: ExecutionContext) -> StepResult:
        """
        执行验证
        
        Config参数:
            check_type: 检查类型 ('length' | 'keywords' | 'format')
            criteria: 验证标准字典
            target_step: 目标步骤ID（默认为前一个步骤）
        """
        try:
            check_type = self.config.get('check_type', 'length')
            criteria = self.config.get('criteria', {})
            target_step = self.config.get('target_step')
            
            # 获取要验证的内容
            if target_step and target_step in context.step_results:
                target_result = context.step_results[target_step]
            else:
                # 使用最后一个步骤的结果
                if not context.step_results:
                    return StepResult(
                        success=False,
                        error="没有可验证的步骤结果"
                    )
                target_result = list(context.step_results.values())[-1]
            
            # 获取要验证的文本
            text_to_validate = ""
            if 'answer' in target_result.data:
                text_to_validate = target_result.data['answer']
            elif 'extracted_text' in target_result.data:
                text_to_validate = target_result.data['extracted_text']
            else:
                return StepResult(
                    success=False,
                    error="目标步骤结果中没有可验证的文本"
                )
            
            logger.info(f"[验证Step] 类型: {check_type}, 文本长度: {len(text_to_validate)}")
            
            # 执行验证
            is_valid = False
            validation_message = ""
            
            if check_type == 'length':
                min_length = criteria.get('min_length', 0)
                max_length = criteria.get('max_length', float('inf'))
                text_length = len(text_to_validate)
                
                is_valid = min_length <= text_length <= max_length
                
                if is_valid:
                    validation_message = f"文本长度 {text_length} 符合要求（{min_length}-{max_length}）"
                else:
                    validation_message = f"文本长度 {text_length} 不符合要求（{min_length}-{max_length}）"
            
            elif check_type == 'keywords':
                required_keywords = criteria.get('required_keywords', [])
                forbidden_keywords = criteria.get('forbidden_keywords', [])
                
                # 检查必需关键词
                missing_keywords = [kw for kw in required_keywords if kw not in text_to_validate]
                # 检查禁止关键词
                found_forbidden = [kw for kw in forbidden_keywords if kw in text_to_validate]
                
                is_valid = (not missing_keywords) and (not found_forbidden)
                
                if is_valid:
                    validation_message = "关键词检查通过"
                else:
                    msg_parts = []
                    if missing_keywords:
                        msg_parts.append(f"缺少关键词: {missing_keywords}")
                    if found_forbidden:
                        msg_parts.append(f"包含禁止关键词: {found_forbidden}")
                    validation_message = "; ".join(msg_parts)
            
            else:
                validation_message = f"不支持的验证类型: {check_type}"
            
            logger.info(f"[验证Step] 结果: {'通过' if is_valid else '失败'} - {validation_message}")
            
            return StepResult(
                success=True,
                data={
                    'valid': is_valid,
                    'message': validation_message,
                    'check_type': check_type,
                },
                metadata={
                    'text_length': len(text_to_validate),
                }
            )
            
        except Exception as e:
            logger.error(f"[验证Step] 执行失败: {e}", exc_info=True)
            return StepResult(
                success=False,
                error=f"验证失败: {str(e)}"
            )
