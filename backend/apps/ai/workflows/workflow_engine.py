"""
工作流编排引擎 - 支持复杂的多步骤AI任务自动化执行

核心功能：
1. 工作流定义和解析
2. 任务依赖管理
3. 步骤并行/串行执行
4. 结果聚合与处理
5. 错误恢复机制
"""

import logging
import time
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class WorkflowStatus(str, Enum):
    """工作流状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    """步骤状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """工作流步骤定义"""
    id: str
    name: str
    function_id: str  # AI功能ID，如 'resume_optimize', 'company_review'
    description: str
    depends_on: List[str] = field(default_factory=list)  # 依赖的步骤ID列表
    optional: bool = False  # 是否可选（失败不影响整体流程）
    status: StepStatus = StepStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None


@dataclass
class WorkflowContext:
    """工作流执行上下文"""
    user: Any  # Django User对象
    workflow_id: str
    initial_input: str  # 用户初始输入
    steps: List[WorkflowStep]
    status: WorkflowStatus = WorkflowStatus.PENDING
    results: Dict[str, Any] = field(default_factory=dict)  # 各步骤结果
    shared_context: Dict[str, Any] = field(default_factory=dict)  # 步骤间共享的上下文
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error: Optional[str] = None


class WorkflowEngine:
    """工作流执行引擎"""
    
    def __init__(self, ai_executor: Callable[[str, str, Dict], str]):
        """
        初始化工作流引擎
        
        Args:
            ai_executor: AI执行函数，签名为 (function_id, question, context) -> answer
        """
        self.ai_executor = ai_executor
        self.workflows: Dict[str, WorkflowContext] = {}
    
    def create_workflow(
        self,
        workflow_id: str,
        user: Any,
        initial_input: str,
        steps: List[Dict[str, Any]]
    ) -> WorkflowContext:
        """
        创建工作流实例
        
        Args:
            workflow_id: 工作流唯一标识
            user: 用户对象
            initial_input: 用户初始输入
            steps: 步骤定义列表
        
        Returns:
            WorkflowContext: 工作流上下文
        """
        workflow_steps = []
        for step_def in steps:
            step = WorkflowStep(
                id=step_def["id"],
                name=step_def["name"],
                function_id=step_def["function_id"],
                description=step_def["description"],
                depends_on=step_def.get("depends_on", []),
                optional=step_def.get("optional", False),
            )
            workflow_steps.append(step)
        
        context = WorkflowContext(
            user=user,
            workflow_id=workflow_id,
            initial_input=initial_input,
            steps=workflow_steps,
        )
        
        self.workflows[workflow_id] = context
        logger.info(f"[工作流] 创建工作流: {workflow_id}, 步骤数: {len(workflow_steps)}")
        
        return context
    
    def execute_workflow(
        self,
        workflow_id: str,
        yield_progress: bool = False
    ):
        """
        执行工作流
        
        Args:
            workflow_id: 工作流ID
            yield_progress: 是否流式返回进度（用于SSE）
        
        Yields:
            Dict: 进度信息（如果 yield_progress=True）
        
        Returns:
            WorkflowContext: 最终工作流上下文
        """
        context = self.workflows.get(workflow_id)
        if not context:
            raise ValueError(f"工作流 {workflow_id} 不存在")
        
        context.status = WorkflowStatus.RUNNING
        context.start_time = time.time()
        
        if yield_progress:
            yield {
                "type": "workflow_start",
                "workflow_id": workflow_id,
                "total_steps": len(context.steps),
            }
        
        try:
            # 拓扑排序执行步骤
            completed_steps = set()
            
            while len(completed_steps) < len(context.steps):
                # 找到所有可以执行的步骤（依赖已完成）
                executable_steps = []
                for step in context.steps:
                    if step.status != StepStatus.COMPLETED and step.status != StepStatus.SKIPPED:
                        if all(dep in completed_steps for dep in step.depends_on):
                            executable_steps.append(step)
                
                if not executable_steps:
                    # 检查是否有循环依赖或无法完成的步骤
                    pending_steps = [s for s in context.steps if s.status == StepStatus.PENDING]
                    if pending_steps:
                        raise Exception(f"工作流死锁：步骤 {[s.id for s in pending_steps]} 无法执行（可能存在循环依赖）")
                    break
                
                # 执行可执行的步骤
                for step in executable_steps:
                    try:
                        # 执行步骤
                        step_result = self._execute_step(context, step)
                        
                        if yield_progress:
                            yield {
                                "type": "step_completed",
                                "step_id": step.id,
                                "step_name": step.name,
                                "status": "success",
                                "result": step_result,
                                "completed": len(completed_steps) + 1,
                                "total": len(context.steps),
                            }
                        
                        completed_steps.add(step.id)
                        context.results[step.id] = step_result
                        
                    except Exception as e:
                        logger.error(f"[工作流] 步骤 {step.id} 执行失败: {e}", exc_info=True)
                        step.status = StepStatus.FAILED
                        step.error = str(e)
                        
                        if yield_progress:
                            yield {
                                "type": "step_failed",
                                "step_id": step.id,
                                "step_name": step.name,
                                "error": str(e),
                            }
                        
                        if not step.optional:
                            # 非可选步骤失败，终止工作流
                            raise Exception(f"关键步骤 {step.name} 失败: {e}")
                        else:
                            # 可选步骤失败，标记为跳过并继续
                            step.status = StepStatus.SKIPPED
                            completed_steps.add(step.id)
            
            # 工作流完成
            context.status = WorkflowStatus.COMPLETED
            context.end_time = time.time()
            elapsed = context.end_time - context.start_time
            
            if yield_progress:
                yield {
                    "type": "workflow_completed",
                    "workflow_id": workflow_id,
                    "elapsed_ms": int(elapsed * 1000),
                    "summary": self._generate_summary(context),
                }
            
            logger.info(f"[工作流] 工作流 {workflow_id} 完成，耗时 {elapsed:.2f}s")
            
            return context
            
        except Exception as e:
            context.status = WorkflowStatus.FAILED
            context.error = str(e)
            context.end_time = time.time()
            
            if yield_progress:
                yield {
                    "type": "workflow_failed",
                    "workflow_id": workflow_id,
                    "error": str(e),
                }
            
            logger.error(f"[工作流] 工作流 {workflow_id} 失败: {e}", exc_info=True)
            raise
    
    def _execute_step(self, context: WorkflowContext, step: WorkflowStep) -> Dict[str, Any]:
        """
        执行单个步骤
        
        Args:
            context: 工作流上下文
            step: 步骤定义
        
        Returns:
            Dict: 步骤执行结果
        """
        step.status = StepStatus.RUNNING
        step.start_time = time.time()
        
        logger.info(f"[工作流] 执行步骤: {step.id} - {step.name}")
        
        # 构建步骤的输入问题
        question = self._build_step_question(context, step)
        
        # 调用AI执行器
        try:
            answer = self.ai_executor(
                function_id=step.function_id,
                question=question,
                context={
                    "workflow_id": context.workflow_id,
                    "step_id": step.id,
                    "user": context.user,
                    "shared_context": context.shared_context,
                    "previous_results": context.results,
                }
            )
            
            step.status = StepStatus.COMPLETED
            step.end_time = time.time()
            step.result = {
                "answer": answer,
                "function_id": step.function_id,
                "elapsed_ms": int((step.end_time - step.start_time) * 1000),
            }
            
            # 更新共享上下文
            context.shared_context[step.id] = answer
            
            return step.result
            
        except Exception as e:
            step.status = StepStatus.FAILED
            step.error = str(e)
            step.end_time = time.time()
            raise
    
    def _build_step_question(self, context: WorkflowContext, step: WorkflowStep) -> str:
        """
        构建步骤的输入问题（基于用户输入和前序步骤结果）
        
        Args:
            context: 工作流上下文
            step: 当前步骤
        
        Returns:
            str: 构建好的问题
        """
        # 基础问题
        question_parts = [f"用户需求：{context.initial_input}\n"]
        
        # 添加步骤描述
        question_parts.append(f"当前任务：{step.description}\n")
        
        # 添加依赖步骤的结果
        if step.depends_on:
            question_parts.append("\n参考信息：")
            for dep_id in step.depends_on:
                if dep_id in context.shared_context:
                    dep_step = next((s for s in context.steps if s.id == dep_id), None)
                    if dep_step:
                        question_parts.append(f"\n【{dep_step.name}的结果】：")
                        question_parts.append(context.shared_context[dep_id][:500])  # 限制长度
        
        return "\n".join(question_parts)
    
    def _generate_summary(self, context: WorkflowContext) -> Dict[str, Any]:
        """
        生成工作流执行摘要
        
        Args:
            context: 工作流上下文
        
        Returns:
            Dict: 摘要信息
        """
        completed_steps = [s for s in context.steps if s.status == StepStatus.COMPLETED]
        failed_steps = [s for s in context.steps if s.status == StepStatus.FAILED]
        skipped_steps = [s for s in context.steps if s.status == StepStatus.SKIPPED]
        
        return {
            "total_steps": len(context.steps),
            "completed": len(completed_steps),
            "failed": len(failed_steps),
            "skipped": len(skipped_steps),
            "steps_summary": [
                {
                    "id": step.id,
                    "name": step.name,
                    "status": step.status.value,
                    "elapsed_ms": int((step.end_time - step.start_time) * 1000) if step.start_time and step.end_time else None,
                }
                for step in context.steps
            ],
        }
    
    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowContext]:
        """获取工作流状态"""
        return self.workflows.get(workflow_id)
    
    def cancel_workflow(self, workflow_id: str):
        """取消工作流执行"""
        context = self.workflows.get(workflow_id)
        if context and context.status == WorkflowStatus.RUNNING:
            context.status = WorkflowStatus.CANCELLED
            context.end_time = time.time()
            logger.info(f"[工作流] 工作流 {workflow_id} 已取消")


# ========== 预定义工作流模板 ==========

def get_workflow_template(template_name: str) -> Optional[List[Dict[str, Any]]]:
    """
    获取预定义的工作流模板
    
    Args:
        template_name: 模板名称
    
    Returns:
        List[Dict]: 步骤定义列表
    """
    templates = {
        "interview_preparation": [
            {
                "id": "analyze_resume",
                "name": "分析简历",
                "function_id": "resume_optimize",
                "description": "分析用户的简历，识别优势和改进点",
                "depends_on": [],
            },
            {
                "id": "research_company",
                "name": "研究目标公司",
                "function_id": "company_review",
                "description": "研究目标公司的背景、文化、业务和面试风格",
                "depends_on": [],
            },
            {
                "id": "prepare_questions",
                "name": "准备面试题",
                "function_id": "mock_interview",
                "description": "根据公司特点和职位要求，生成模拟面试题",
                "depends_on": ["research_company"],
            },
            {
                "id": "career_planning",
                "name": "职业规划建议",
                "function_id": "career_planning",
                "description": "基于简历分析和公司研究，提供职业发展建议",
                "depends_on": ["analyze_resume", "research_company"],
            },
        ],
        
        "course_planning": [
            {
                "id": "query_courses",
                "name": "查询课程",
                "function_id": "course_query",
                "description": "查询专业相关的课程列表和课程要求",
                "depends_on": [],
            },
            {
                "id": "check_prerequisites",
                "name": "检查先修要求",
                "function_id": "academic_qa",
                "description": "分析课程的先修要求和学分要求",
                "depends_on": ["query_courses"],
            },
            {
                "id": "suggest_order",
                "name": "推荐学习顺序",
                "function_id": "study_method",
                "description": "根据先修要求和课程难度，推荐最优学习顺序",
                "depends_on": ["query_courses", "check_prerequisites"],
            },
        ],
        
        "startup_launch": [
            {
                "id": "validate_idea",
                "name": "验证创意",
                "function_id": "idea_validation",
                "description": "评估创业想法的可行性和创新性",
                "depends_on": [],
            },
            {
                "id": "market_analysis",
                "name": "市场分析",
                "function_id": "market_analysis",
                "description": "分析目标市场规模、增长趋势和机会",
                "depends_on": [],
            },
            {
                "id": "competitor_analysis",
                "name": "竞争分析",
                "function_id": "competitor_analysis",
                "description": "分析竞争对手的优劣势",
                "depends_on": ["market_analysis"],
            },
            {
                "id": "business_plan",
                "name": "制定商业计划",
                "function_id": "business_plan",
                "description": "整合前期分析，制定完整的商业计划",
                "depends_on": ["validate_idea", "market_analysis", "competitor_analysis"],
            },
        ],
        
        "academic_research": [
            {
                "id": "research_topic",
                "name": "研究主题",
                "function_id": "academic_qa",
                "description": "理解研究主题和核心问题",
                "depends_on": [],
            },
            {
                "id": "gather_references",
                "name": "收集文献",
                "function_id": "citation_format",
                "description": "收集和整理相关文献资料",
                "depends_on": ["research_topic"],
            },
            {
                "id": "draft_paper",
                "name": "撰写草稿",
                "function_id": "paper_polish",
                "description": "基于文献和研究，撰写论文草稿",
                "depends_on": ["research_topic", "gather_references"],
            },
            {
                "id": "check_plagiarism",
                "name": "查重检查",
                "function_id": "plagiarism_check",
                "description": "检查论文的原创性",
                "depends_on": ["draft_paper"],
                "optional": True,
            },
        ],
    }
    
    return templates.get(template_name)



