"""
WorkflowOrchestrator - 工作流编排引擎核心
"""

import logging
import time
import uuid
from typing import Dict, Any, List, Optional
from enum import Enum

from .config_loader import WorkflowConfig
from .step_registry import StepRegistry
from .steps.base_step import ExecutionContext, StepResult

logger = logging.getLogger(__name__)


class WorkflowStatus(str, Enum):
    """工作流状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class StepExecutionRecord:
    """步骤执行记录"""
    def __init__(self, step_id: str, name: str):
        self.step_id = step_id
        self.name = name
        self.status = "pending"
        self.start_time = None
        self.end_time = None
        self.result = None
        self.error = None


class WorkflowOrchestrator:
    """工作流编排引擎"""
    
    def __init__(self):
        """初始化Orchestrator"""
        self.active_workflows: Dict[str, Any] = {}
        logger.info("[Orchestrator] 工作流编排引擎初始化完成")
    
    def execute_workflow(
        self,
        workflow_config: WorkflowConfig,
        context: ExecutionContext,
        yield_progress: bool = False
    ):
        """
        执行工作流
        
        Args:
            workflow_config: 工作流配置
            context: 执行上下文
            yield_progress: 是否流式返回进度
        
        Yields:
            Dict: 进度信息
        
        Returns:
            ExecutionContext: 最终执行上下文
        """
        workflow_id = context.workflow_id
        self.active_workflows[workflow_id] = {
            'status': WorkflowStatus.RUNNING,
            'start_time': time.time(),
        }
        
        if yield_progress:
            yield {
                'type': 'workflow_start',
                'workflow_id': workflow_id,
                'workflow_name': workflow_config.name,
                'total_steps': len(workflow_config.steps),
            }
        
        try:
            # 创建步骤执行记录
            step_records = {}
            for step_config in workflow_config.steps:
                step_records[step_config.id] = StepExecutionRecord(
                    step_id=step_config.id,
                    name=step_config.name,
                )
            
            # 拓扑排序执行步骤
            completed_steps = set()
            total_steps = len(workflow_config.steps)
            
            while len(completed_steps) < total_steps:
                # 找到可执行的步骤
                executable_steps = []
                for step_config in workflow_config.steps:
                    if step_config.id in completed_steps:
                        continue
                    
                    # 检查依赖是否都已完成
                    if all(dep in completed_steps for dep in step_config.dependencies):
                        executable_steps.append(step_config)
                
                if not executable_steps:
                    # 检查是否有死锁
                    pending = [s.id for s in workflow_config.steps if s.id not in completed_steps]
                    raise Exception(f"工作流死锁，无法执行步骤: {pending}")
                
                # 执行可执行的步骤
                for step_config in executable_steps:
                    try:
                        # 执行步骤
                        result = self._execute_step(step_config, context)
                        
                        step_records[step_config.id].status = "completed"
                        step_records[step_config.id].result = result
                        context.step_results[step_config.id] = result
                        
                        if yield_progress:
                            yield {
                                'type': 'step_completed',
                                'step_id': step_config.id,
                                'step_name': step_config.name,
                                'status': 'success',
                                'result': {
                                    'success': result.success,
                                    'data_keys': list(result.data.keys()),
                                },
                                'completed': len(completed_steps) + 1,
                                'total': total_steps,
                            }
                        
                        completed_steps.add(step_config.id)
                        
                    except Exception as e:
                        logger.error(f"[Orchestrator] 步骤 {step_config.id} 执行失败: {e}", exc_info=True)
                        
                        step_records[step_config.id].status = "failed"
                        step_records[step_config.id].error = str(e)
                        
                        if yield_progress:
                            yield {
                                'type': 'step_failed',
                                'step_id': step_config.id,
                                'step_name': step_config.name,
                                'error': str(e),
                            }
                        
                        if not step_config.optional:
                            # 非可选步骤失败，终止工作流
                            raise Exception(f"关键步骤 {step_config.name} 失败: {e}")
                        else:
                            # 可选步骤失败，标记为完成并继续
                            completed_steps.add(step_config.id)
            
            # 工作流完成
            self.active_workflows[workflow_id]['status'] = WorkflowStatus.COMPLETED
            self.active_workflows[workflow_id]['end_time'] = time.time()
            elapsed = self.active_workflows[workflow_id]['end_time'] - self.active_workflows[workflow_id]['start_time']
            
            if yield_progress:
                yield {
                    'type': 'workflow_completed',
                    'workflow_id': workflow_id,
                    'elapsed_ms': int(elapsed * 1000),
                    'total_steps': total_steps,
                    'completed_steps': len(completed_steps),
                }
            
            logger.info(f"[Orchestrator] 工作流 {workflow_id} 完成，耗时 {elapsed:.2f}s")
            return context
            
        except Exception as e:
            self.active_workflows[workflow_id]['status'] = WorkflowStatus.FAILED
            self.active_workflows[workflow_id]['end_time'] = time.time()
            
            if yield_progress:
                yield {
                    'type': 'workflow_failed',
                    'workflow_id': workflow_id,
                    'error': str(e),
                }
            
            logger.error(f"[Orchestrator] 工作流 {workflow_id} 失败: {e}", exc_info=True)
            raise
    
    def _execute_step(self, step_config, context: ExecutionContext) -> StepResult:
        """
        执行单个步骤
        
        Args:
            step_config: 步骤配置
            context: 执行上下文
        
        Returns:
            StepResult: 步骤结果
        """
        start_time = time.time()
        logger.info(f"[Orchestrator] 执行步骤: {step_config.id} - {step_config.name}")
        
        # 从注册表获取Step类
        step_class = StepRegistry.get_step(step_config.type)
        
        # 创建Step实例
        step_instance = step_class(
            step_id=step_config.id,
            name=step_config.name,
            description=step_config.description,
            config=step_config.config,
        )
        
        # 执行步骤
        result = step_instance.execute(context)
        
        elapsed = time.time() - start_time
        logger.info(
            f"[Orchestrator] 步骤 {step_config.id} 完成: "
            f"成功={result.success}, 耗时={elapsed:.2f}s"
        )
        
        return result


# 全局Orchestrator实例
_orchestrator_instance = None


def get_orchestrator() -> WorkflowOrchestrator:
    """获取Orchestrator单例"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = WorkflowOrchestrator()
    return _orchestrator_instance
