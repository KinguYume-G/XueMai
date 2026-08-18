"""
LLM生成Step - 调用AI模型生成回答
"""

from typing import Dict, Any
import logging

from .base_step import BaseStep, StepResult, ExecutionContext

logger = logging.getLogger(__name__)


class LLMGenerateStep(BaseStep):
    """LLM文本生成步骤"""
    
    def execute(self, context: ExecutionContext) -> StepResult:
        """
        执行LLM生成
        
        Config参数:
            function_id: AI功能ID（如 'resume_optimize'）
            prompt_template: Prompt模板（支持变量替换）
            use_rag_context: 是否使用RAG上下文（默认False）
            input_variables: 输入变量字典
        """
        try:
           # 获取配置
            function_id = self.config.get('function_id', 'general')
            prompt_template = self.config.get('prompt_template')
            use_rag_context = self.config.get('use_rag_context', False)
            input_vars = self.config.get('input_variables', {})
            
            # 加载AI client和配置
            from apps.ai.clients import get_ai_client
            from apps.ai.views import get_function_config, get_system_prompt
            
            ai_client = get_ai_client()
            func_config = get_function_config(function_id)
            
            # 加载system prompt
            system_prompt_file = func_config.get("system_prompt_file", "prompts/generic.txt")
            system_prompt = get_system_prompt(system_prompt_file)
            
            # 构建用户prompt
            if prompt_template:
                # 解析输入变量中的模板
                resolved_vars = {}
                for key, value_template in input_vars.items():
                    resolved_vars[key] = self._resolve_variable(str(value_template), context)
                
                # 构建用户消息
                user_message = prompt_template
                for key, value in resolved_vars.items():
                    user_message = user_message.replace(f"{{{{{key}}}}}", value)
            else:
                user_message = context.initial_input
            
            # 如果需要RAG上下文
            if use_rag_context:
                rag_context = ""
                # 查找前序RAG步骤的结果
                for step_id, result in context.step_results.items():
                    if 'context' in result.data:
                        rag_context = result.data['context']
                        break
                
                if rag_context:
                    system_prompt = f"{system_prompt}\n\n参考资料：\n{rag_context}"
                    logger.info(f"[LLM生成Step] 使用RAG上下文，长度: {len(rag_context)}")
            
            # 构建消息
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ]
            
            logger.info(f"[LLM生成Step] 调用 {function_id}, prompt长度: {len(user_message)}")
            
            # 调用AI生成
            answer = ai_client.chat_completion(messages=messages)
            
            logger.info(f"[LLM生成Step] 生成完成，回答长度: {len(answer)}")
            
            return StepResult(
                success=True,
                data={
                    'answer': answer,
                    'function_id': function_id,
                    'prompt_length': len(user_message),
                    'answer_length': len(answer),
                },
                metadata={
                    'used_rag': use_rag_context,
                }
            )
            
        except Exception as e:
            logger.error(f"[LLM生成Step] 执行失败: {e}", exc_info=True)
            return StepResult(
                success=False,
                error=f"LLM生成失败: {str(e)}"
            )
