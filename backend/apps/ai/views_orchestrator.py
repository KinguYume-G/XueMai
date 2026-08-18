"""
Orchestrator API视图
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status as http_status
from django.http import StreamingHttpResponse
import json
import logging
import uuid

from apps.ai.orchestrator import get_orchestrator, WorkflowConfigLoader, ExecutionContext
from apps.ai.models import AIDocument
from apps.ai.services.intent_recognizer import get_intent_recognizer

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def orchestrator_execute_stream(request):
    """
    执行Orchestrator工作流（流式返回进度）
    
    Request body:
    {
        "question": "帮我优化简历",
        "document_ids": [123],
        "workflow_name": "resume_optimization",  // 可选
        "variables": {"industry": "tech"}  // 可选
    }
    
    Response: SSE流式返回
    """
    try:
        question = request.data.get('question')
        document_ids = request.data.get('document_ids', [])
        workflow_name = request.data.get('workflow_name')
        variables = request.data.get('variables', {})
        
        if not question:
            return Response(
                {'error': '问题不能为空'},
                status=http_status.HTTP_400_BAD_REQUEST
            )
        
        logger.info(
            f"[Orchestrator API] 用户: {request.user.username}, "
            f"问题: {question[:50]}..., 文档数: {len(document_ids)}"
        )
        
        # 1. 加载上传的文档
        uploaded_documents = []
        if document_ids:
            uploaded_documents = list(AIDocument.objects.filter(
                id__in=document_ids,
                uploaded_by=request.user
            ))
            logger.info(f"[Orchestrator API] 找到 {len(uploaded_documents)} 个文档")
        
        # 2. 获取工作流配置
        workflow_config = None
        
        if workflow_name:
            # 直接加载指定的工作流
            try:
                workflow_config = WorkflowConfigLoader.load_from_yaml(
                    f"apps/ai/workflows/{workflow_name}.yaml"
                )
            except Exception as e:
                return Response(
                    {'error': f'工作流配置加载失败: {e}'},
                    status=http_status.HTTP_404_NOT_FOUND
                )
        else:
            # 自动匹配工作流
            recognizer = get_intent_recognizer()
            intent = recognizer.recognize(question, mode='smart')
            
            workflow_config = WorkflowConfigLoader.find_matching_workflow(
                function_id=intent.function_id,
                has_file_upload=bool(uploaded_documents)
            )
            
            if not workflow_config:
                return Response(
                    {'error': f'未找到匹配的工作流（function_id={intent.function_id}）'},
                    status=http_status.HTTP_404_NOT_FOUND
                )
        
        logger.info(f"[Orchestrator API] 使用工作流: {workflow_config.name}")
        
        # 3. 创建执行上下文
        workflow_id = str(uuid.uuid4())
        context = ExecutionContext(
            user=request.user,
            workflow_id=workflow_id,
            initial_input=question,
            uploaded_files=uploaded_documents,
            variables=variables,
        )
        
        # 4. 执行工作流（流式返回）
        def generate():
            try:
                orchestrator = get_orchestrator()
                for progress in orchestrator.execute_workflow(workflow_config, context, yield_progress=True):
                    yield f"data: {json.dumps(progress, ensure_ascii=False)}\\n\\n"
                
                # 发送完成后的最终结果
                final_result = {
                    'type': 'final_result',
                    'workflow_id': workflow_id,
                    'results': {}
                }
                
                # 提取关键结果
                for step_id, step_result in context.step_results.items():
                    if step_result.success and 'answer' in step_result.data:
                        final_result['results']['answer'] = step_result.data['answer']
                        break
                
                yield f"data: {json.dumps(final_result, ensure_ascii=False)}\\n\\n"
                yield f"data: [DONE]\\n\\n"
                
            except Exception as e:
                logger.error(f"[Orchestrator API] 执行失败: {e}", exc_info=True)
                error_msg = {'type': 'error', 'message': str(e)}
                yield f"data: {json.dumps(error_msg, ensure_ascii=False)}\\n\\n"
        
        response = StreamingHttpResponse(generate(), content_type="text/event-stream")
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response
        
    except Exception as e:
        logger.error(f"[Orchestrator API] 请求处理失败: {e}", exc_info=True)
        return Response(
            {'error': '服务器内部错误'},
            status=http_status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def orchestrator_workflows_list(request):
    """
    获取所有可用的工作流列表
    
    Response:
    {
        "workflows": [
            {
                "name": "resume_optimization",
                "description": "简历优化流程",
                "steps_count": 4,
                "trigger_conditions": {...}
            }
        ]
    }
    """
    try:
        workflows_dict = WorkflowConfigLoader.load_all_workflows()
        
        workflows = []
        for name, config in workflows_dict.items():
            workflows.append({
                'name': config.name,
                'description': config.description,
                'steps_count': len(config.steps),
                'trigger_conditions': config.trigger_conditions,
                'metadata': config.metadata,
            })
        
        return Response({'workflows': workflows})
        
    except Exception as e:
        logger.error(f"[Orchestrator API] 获取工作流列表失败: {e}", exc_info=True)
        return Response(
            {'error': '获取工作流列表失败'},
            status=http_status.HTTP_500_INTERNAL_SERVER_ERROR
        )
