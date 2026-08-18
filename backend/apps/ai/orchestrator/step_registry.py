"""
Step注册表 - 管理所有可用的Step类型
"""

from typing import Dict, Type
import logging

from .steps.base_step import BaseStep
from .steps.rag_retrieve_step import RAGRetrieveStep
from .steps.llm_generate_step import LLMGenerateStep
from .steps.file_process_step import FileProcessStep
from .steps.validation_step import ValidationStep

logger = logging.getLogger(__name__)


class StepRegistry:
    """Step注册表"""
    
    _registry: Dict[str, Type[BaseStep]] = {}
    
    @classmethod
    def register(cls, step_type: str, step_class: Type[BaseStep]):
        """
        注册Step类型
        
        Args:
            step_type: Step类型标识
            step_class: Step类
        """
        cls._registry[step_type] = step_class
        logger.info(f"[StepRegistry] 注册Step类型: {step_type} -> {step_class.__name__}")
    
    @classmethod
    def get_step(cls, step_type: str) -> Type[BaseStep]:
        """
        获取Step类
        
        Args:
            step_type: Step类型标识
        
        Returns:
            Type[BaseStep]: Step类
        
        Raises:
            ValueError: Step类型不存在
        """
        if step_type not in cls._registry:
            raise ValueError(f"未知的Step类型: {step_type}")
        return cls._registry[step_type]
    
    @classmethod
    def list_available_steps(cls) -> list:
        """
        列出所有可用的Step类型
        
        Returns:
            list: Step类型列表
        """
        return list(cls._registry.keys())


# 注册内置Step类型
StepRegistry.register('rag_retrieve', RAGRetrieveStep)
StepRegistry.register('llm_generate', LLMGenerateStep)
StepRegistry.register('file_process', FileProcessStep)
StepRegistry.register('validation', ValidationStep)

logger.info(f"[StepRegistry] 已注册 {len(StepRegistry.list_available_steps())} 个Step类型")
