"""
YAML工作流配置加载器
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class StepConfig:
    """步骤配置"""
    id: str
    type: str
    name: str
    description: str
    config: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    optional: bool = False


@dataclass
class WorkflowConfig:
    """工作流配置"""
    name: str
    description: str
    steps: List[StepConfig]
    trigger_conditions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowConfigLoader:
    """YAML工作流配置加载器"""
    
    @staticmethod
    def load_from_yaml(file_path: str) -> WorkflowConfig:
        """
        从YAML文件加载工作流配置
        
        Args:
            file_path: YAML文件路径
        
        Returns:
            WorkflowConfig: 工作流配置对象
        
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: YAML格式错误
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"工作流配置文件不存在: {file_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # 解析步骤配置
            steps = []
            for step_data in data.get('steps', []):
                step = StepConfig(
                    id=step_data['id'],
                    type=step_data['type'],
                    name=step_data['name'],
                    description=step_data.get('description', ''),
                    config=step_data.get('config', {}),
                    dependencies=step_data.get('dependencies', []),
                    optional=step_data.get('optional', False),
                )
                steps.append(step)
            
            workflow = WorkflowConfig(
                name=data['name'],
                description=data.get('description', ''),
                steps=steps,
                trigger_conditions=data.get('trigger_conditions', {}),
                metadata=data.get('metadata', {}),
            )
            
            logger.info(f"[ConfigLoader] 加载工作流: {workflow.name}, 步骤数: {len(steps)}")
            return workflow
            
        except yaml.YAMLError as e:
            raise ValueError(f"YAML解析失败: {e}")
        except KeyError as e:
            raise ValueError(f"工作流配置缺少必需字段: {e}")
    
    @staticmethod
    def load_all_workflows(directory: str = None) -> Dict[str, WorkflowConfig]:
        """
        加载目录中的所有工作流配置
        
        Args:
            directory: 工作流配置目录，默认为 apps/ai/workflows/
        
        Returns:
            Dict[str, WorkflowConfig]: 工作流名称 -> 配置对象的字典
        """
        if directory is None:
            # 默认目录
            base_dir = Path(__file__).parent.parent / 'workflows'
        else:
            base_dir = Path(directory)
        
        if not base_dir.exists():
            logger.warning(f"工作流配置目录不存在: {base_dir}")
            return {}
        
        workflows = {}
        for yaml_file in base_dir.glob('*.yaml'):
            try:
                workflow = WorkflowConfigLoader.load_from_yaml(str(yaml_file))
                workflows[workflow.name] = workflow
                logger.info(f"[ConfigLoader] 加载工作流配置: {workflow.name}")
            except Exception as e:
                logger.error(f"[ConfigLoader] 加载 {yaml_file.name} 失败: {e}")
        
        logger.info(f"[ConfigLoader] 共加载 {len(workflows)} 个工作流配置")
        return workflows
    
    @staticmethod
    def find_matching_workflow(
        function_id: str,
        has_file_upload: bool = False,
        workflows: Dict[str, WorkflowConfig] = None
    ) -> Optional[WorkflowConfig]:
        """
        根据条件查找匹配的工作流
        
        Args:
            function_id: AI功能ID
            has_file_upload: 是否有文件上传
            workflows: 工作流配置字典（可选，默认加载所有）
        
        Returns:
            Optional[WorkflowConfig]: 匹配的工作流配置，找不到返回None
        """
        if workflows is None:
            workflows = WorkflowConfigLoader.load_all_workflows()
        
        for name, workflow in workflows.items():
            conditions = workflow.trigger_conditions
            
            # 检查function_id匹配
            if 'function_ids' in conditions:
                if function_id not in conditions['function_ids']:
                    continue
            
            # 检查文件上传要求
            if 'has_file_upload' in conditions:
                if conditions['has_file_upload'] != has_file_upload:
                    continue
            
            logger.info(f"[ConfigLoader] 找到匹配工作流: {name} (function_id={function_id})")
            return workflow
        
        logger.info(f"[ConfigLoader] 未找到匹配工作流 (function_id={function_id})")
        return None
