"""
Orchestrator步骤基类

所有工作流步骤都继承此抽象基类
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class StepResult:
    """步骤执行结果"""
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionContext:
    """工作流执行上下文"""
    user: Any  # Django User对象
    workflow_id: str
    initial_input: str  # 用户初始输入
    uploaded_files: List[Any] = field(default_factory=list)  # AIDocument对象列表
    step_results: Dict[str, StepResult] = field(default_factory=dict)  # 各步骤结果
    shared_data: Dict[str, Any] = field(default_factory=dict)  # 步骤间共享数据
    variables: Dict[str, Any] = field(default_factory=dict)  # 用户自定义变量


class BaseStep(ABC):
    """
    工作流步骤抽象基类
    
    所有Step实现必须继承此类并实现execute方法
    """
    
    def __init__(self, step_id: str, name: str, description: str, config: Dict[str, Any]):
        """
        初始化步骤
        
        Args:
            step_id: 步骤唯一标识
            name: 步骤名称
            description: 步骤描述
            config: 步骤配置参数（从YAML加载）
        """
        self.step_id = step_id
        self.name = name
        self.description = description
        self.config = config
    
    @abstractmethod
    def execute(self, context: ExecutionContext) -> StepResult:
        """
        执行步骤逻辑
        
        Args:
            context: 工作流执行上下文
        
        Returns:
            StepResult: 执行结果
        """
        pass
    
    def validate_input(self, context: ExecutionContext) -> bool:
        """
        验证输入是否满足步骤要求
        
        Args:
            context: 工作流执行上下文
        
        Returns:
            bool: 验证是否通过
        """
        return True
    
    def get_dependencies(self) -> List[str]:
        """
        获取步骤依赖的其他步骤ID
        
        Returns:
            List[str]: 依赖步骤ID列表
        """
        return self.config.get('dependencies', [])
    
    def is_optional(self) -> bool:
        """
        判断步骤是否可选（失败不影响整体流程）
        
        Returns:
            bool: 是否可选
        """
        return self.config.get('optional', False)
    
    def _resolve_variable(self, template: str, context: ExecutionContext) -> str:
        """
        解析模板变量 {{variable_name}} 或 {{step_id.field}}
        
        Args:
            template: 模板字符串
            context: 执行上下文
        
        Returns:
            str: 解析后的字符串
        """
        import re
        
        # 匹配 {{var}} 格式
        pattern = r'\{\{([\w\.]+)\}\}'
        
        def replacer(match):
            var_path = match.group(1).strip()
            
            # 处理 step_id.field 格式
            if '.' in var_path:
                step_id, field = var_path.split('.', 1)
                if step_id in context.step_results:
                    result = context.step_results[step_id]
                    # 支持嵌套字段访问
                    value = result.data
                    for part in field.split('.'):
                        if isinstance(value, dict) and part in value:
                            value = value[part]
                        else:
                            logger.warning(f"变量 {var_path} 未找到")
                            return match.group(0)
                    return str(value)
            
            # 处理简单变量
            if var_path in context.variables:
                return str(context.variables[var_path])
            if var_path in context.shared_data:
                return str(context.shared_data[var_path])
            if var_path == 'user_input':
                return context.initial_input
            
            logger.warning(f"变量 {var_path} 未找到")
            return match.group(0)
        
        return re.sub(pattern, replacer, template)
