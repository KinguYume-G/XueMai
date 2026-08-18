"""
工作流相关的API视图

提供以下端点：
- POST /api/ai/workflow/execute/ - 执行工作流（流式）
- GET /api/ai/workflow/templates/ - 获取工作流模板列表
- GET /api/ai/workflow/status/<workflow_id>/ - 获取工作流状态
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status as http_status
from django.http import StreamingHttpResponse
import json
import logging
import uuid

from apps.ai.workflows.workflow_engine import WorkflowEngine, get_workflow_template
from apps.ai.clients import get_ai_client
from apps.ai.services.rag_engine import RAGEngine
from apps.ai.views import get_function_config, get_system_prompt

logger = logging.getLogger(__name__)

# 全局工作流引擎实例
_workflow_engine = None


def get_workflow_engine():
    """获取工作流引擎单例"""
    global _workflow_engine
    if _workflow_engine is None:
        # 创建AI执行器
        def ai_executor(function_id: str, question: str, context: dict) -> str:
            """AI执行器：调用AI功能生成回答"""
            try:
                ai_client = get_ai_client()
                func_config = get_function_config(function_id)
                
                # 加载system prompt
                system_prompt = get_system_prompt(
                    func_config.get("system_prompt_file", "prompts/generic.txt")
                )
                
                # RAG支持
                use_rag = func_config.get("enable_rag", False)
                enhanced_system = system_prompt
                
                if use_rag:
                    try:
                        rag_engine = RAGEngine()
                        docs = rag_engine.retrieve(query=question, top_k=3)
                        if docs:
                            context_parts = []
                            for i, doc in enumerate(docs, 1):
                                source = doc.metadata.get("title", "未知来源")
                                context_parts.append(
                                    f"【参考资料 {i}】\n来源：{source}\n内容：{doc.page_content}\n"
                                )
                            rag_context = "\n".join(context_parts)
                            enhanced_system = f"{system_prompt}\n\n参考资料：\n{rag_context}"
                    except Exception as e:
                        logger.warning(f"[工作流] RAG检索失败: {e}")
                
                # 构建消息
                messages = [
                    {"role": "system", "content": enhanced_system},
                    {"role": "user", "content": question},
                ]
                
                # 生成回答
                answer = ai_client.chat_completion(messages=messages)
                return answer
                
            except Exception as e:
                logger.error(f"[工作流] AI执行器失败: {e}", exc_info=True)
                raise RuntimeError("AI execution failed") from e
        
        _workflow_engine = WorkflowEngine(ai_executor=ai_executor)
    
    return _workflow_engine


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def workflow_execute_stream(request):
    """
    执行工作流（流式返回进度）
    
    Request body:
    {
        "workflow_type": "interview_preparation",  # 工作流类型或模板名称
        "input": "帮我准备Google软件工程师面试",
        "custom_steps": [...]  # 可选，自定义步骤列表
    }
    
    Response: SSE流式返回
    """
    try:
        workflow_type = request.data.get('workflow_type')
        user_input = request.data.get('input')
        custom_steps = request.data.get('custom_steps')
        
        if not user_input:
            return Response(
                {'error': '用户输入不能为空'},
                status=http_status.HTTP_400_BAD_REQUEST
            )
        
        # 获取步骤定义
        if custom_steps:
            steps = custom_steps
        elif workflow_type:
            steps = get_workflow_template(workflow_type)
            if not steps:
                return Response(
                    {'error': f'工作流模板 {workflow_type} 不存在'},
                    status=http_status.HTTP_404_NOT_FOUND
                )
        else:
            # 自动检测工作流类型
            workflow_type = _detect_workflow_type(user_input)
            steps = get_workflow_template(workflow_type)
            if not steps:
                return Response(
                    {'error': '无法识别工作流类型'},
                    status=http_status.HTTP_400_BAD_REQUEST
                )
        
        # 创建工作流
        workflow_id = str(uuid.uuid4())
        engine = get_workflow_engine()
        
        engine.create_workflow(
            workflow_id=workflow_id,
            user=request.user,
            initial_input=user_input,
            steps=steps,
        )
        
        logger.info(
            f"[工作流API] 用户 {request.user.username} 启动工作流: {workflow_type}, "
            f"ID: {workflow_id}, 步骤数: {len(steps)}"
        )
        
        # 流式执行工作流
        def generate():
            try:
                for progress in engine.execute_workflow(workflow_id, yield_progress=True):
                    yield f"data: {json.dumps(progress, ensure_ascii=False)}\n\n"
                
                # 发送完成信号
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"[工作流API] 执行失败: {e}", exc_info=True)
                error_payload = {
                    "type": "error",
                    "message": "Workflow execution failed",
                }
                yield f"data: {json.dumps(error_payload, ensure_ascii=False)}\n\n"
        
        response = StreamingHttpResponse(generate(), content_type="text/event-stream")
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response
        
    except Exception as e:
        logger.error(f"[工作流API] 请求处理失败: {e}", exc_info=True)
        return Response(
            {'error': '服务器内部错误'},
            status=http_status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def workflow_templates_list(request):
    """
    获取所有工作流模板列表
    
    Response:
    {
        "templates": [
            {
                "id": "interview_preparation",
                "name": "面试准备助手",
                "description": "帮助准备面试的完整流程",
                "steps_count": 4,
                "estimated_time_minutes": 10
            }
        ]
    }
    """
    templates = [
        {
            "id": "interview_preparation",
            "name": "面试准备助手",
            "description": "分析简历、研究公司、准备面试题、制定职业规划",
            "steps_count": 4,
            "estimated_time_minutes": 10,
            "keywords": ["面试", "求职", "职业"],
            "icon": "🎤",
        },
        {
            "id": "course_planning",
            "name": "课程规划助手",
            "description": "查询课程、分析先修要求、推荐学习顺序",
            "steps_count": 3,
            "estimated_time_minutes": 5,
            "keywords": ["课程", "选课", "学习"],
            "icon": "📚",
        },
        {
            "id": "startup_launch",
            "name": "创业启动助手",
            "description": "验证创意、市场分析、竞争分析、制定商业计划",
            "steps_count": 4,
            "estimated_time_minutes": 15,
            "keywords": ["创业", "商业计划", "市场"],
            "icon": "🚀",
        },
        {
            "id": "academic_research",
            "name": "学术研究助手",
            "description": "研究主题、收集文献、撰写论文、查重检查",
            "steps_count": 4,
            "estimated_time_minutes": 20,
            "keywords": ["论文", "研究", "学术"],
            "icon": "📝",
        },
    ]
    
    return Response({"templates": templates})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def workflow_status(request, workflow_id):
    """
    获取工作流执行状态
    
    Response:
    {
        "workflow_id": "...",
        "status": "running",
        "progress": 0.5,
        "completed_steps": 2,
        "total_steps": 4,
        "current_step": "准备面试题",
        "results": {...}
    }
    """
    try:
        engine = get_workflow_engine()
        context = engine.get_workflow_status(workflow_id)
        
        if not context:
            return Response(
                {'error': '工作流不存在'},
                status=http_status.HTTP_404_NOT_FOUND
            )

        context_user_id = getattr(context.user, "pk", None)
        if not request.user.is_staff and context_user_id != request.user.pk:
            return Response(
                {"error": "You do not have permission to access this workflow."},
                status=http_status.HTTP_403_FORBIDDEN,
            )
        
        # 计算进度
        completed = sum(1 for s in context.steps if s.status == "completed")
        total = len(context.steps)
        progress = completed / total if total > 0 else 0
        
        # 获取当前步骤
        current_step = next((s for s in context.steps if s.status == "running"), None)
        
        return Response({
            "workflow_id": workflow_id,
            "status": context.status.value,
            "progress": progress,
            "completed_steps": completed,
            "total_steps": total,
            "current_step": current_step.name if current_step else None,
            "results": context.results,
            "error": "Workflow execution failed" if context.error else None,
        })
        
    except Exception as e:
        logger.error(f"[工作流API] 获取状态失败: {e}", exc_info=True)
        return Response(
            {'error': '获取状态失败'},
            status=http_status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _detect_workflow_type(user_input: str) -> str:
    """
    自动检测工作流类型（基于关键词匹配）
    
    Args:
        user_input: 用户输入
    
    Returns:
        str: 工作流类型
    """
    input_lower = user_input.lower()
    
    # 面试相关
    if any(kw in input_lower for kw in ["面试", "求职", "简历", "职业规划"]):
        return "interview_preparation"
    
    # 课程相关
    if any(kw in input_lower for kw in ["课程", "选课", "学习计划", "课表"]):
        return "course_planning"
    
    # 创业相关
    if any(kw in input_lower for kw in ["创业", "商业计划", "市场分析", "竞争"]):
        return "startup_launch"
    
    # 学术研究
    if any(kw in input_lower for kw in ["论文", "研究", "文献", "学术"]):
        return "academic_research"
    
    # 默认：面试准备（最常用）
    return "interview_preparation"
