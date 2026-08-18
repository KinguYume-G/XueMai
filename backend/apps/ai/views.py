"""
AI视图 - 提供AI聊天和RAG查询功能
使用统一的 AI 客户端接口 + 智能意图识别 + RAG 混合模式
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import StreamingHttpResponse
from django.db.models import Count
import json
import logging
import time
from pathlib import Path
import yaml

from .clients import get_ai_client
from .models import AIRoutingLog, AIConversation, AIMessage
from .services.intent_recognizer import get_intent_recognizer
from .services.rag_engine import RAGEngine
from .services.context_manager import get_context_manager
from .services.prompt_manager import get_prompt_manager
from .services.search_service import get_search_service
from .services.content_moderator import get_content_moderator
from .workflows.workflow_engine import WorkflowEngine, get_workflow_template

logger = logging.getLogger(__name__)


# ========== 配置加载函数 ==========
_functions_config = None

def load_functions_config():
    """加载AI功能配置"""
    global _functions_config
    if _functions_config is None:
        config_path = Path(__file__).parent / "config" / "functions.yaml"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                _functions_config = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load functions config: {e}")
            _functions_config = {"functions": []}
    return _functions_config

def get_function_config(function_id: str):
    """获取指定AI功能的配置"""
    config = load_functions_config()
    for func in config.get('functions', []):
        if func['id'] == function_id:
            return func
    # Return default config if not found
    return {
        "id": function_id,
        "name": "General Chat",
        "system_prompt_file": "prompts/generic.txt",
        "enable_rag": False
    }

def get_system_prompt(prompt_file: str, variables: dict = None):
    """
    加载system prompt文件并支持动态变量
    
    Args:
        prompt_file: Prompt 文件路径
        variables: 动态变量字典，如 {"user_name": "张三", "university": "APU"}
    
    Returns:
        渲染后的 Prompt 文本
    """
    try:
        prompt_manager = get_prompt_manager()
        
        # 如果是完整路径，提取文件名
        if "/" in prompt_file:
            prompt_file = prompt_file.split("/")[-1]
        
        # 渲染 Prompt
        return prompt_manager.render_prompt(prompt_file, variables or {})
    except Exception as e:
        logger.error(f"Failed to load prompt file {prompt_file}: {e}")
        return "You are a helpful AI assistant."


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_chat_stream(request):
    """
    流式AI聊天API (支持智能意图识别 + RAG)
    
    Request body:
    {
        "question": "用户的问题",
        "mode": "course_query",  # 可选，不提供则自动识别
        "use_rag": true/false     # 可选，覆盖函数配置
    }
    
    Response: Server-Sent Events (SSE) stream
    """
    try:
        data = request.data
        # 获取参数
        question = data.get('question')
        mode = data.get('mode', 'smart')  # smart | exact
        use_rag = data.get('use_rag', None)
        conversation_id = data.get('conversation_id')
        document_ids = data.get('document_ids', [])
        
        if not question:
            return Response({'error': '问题不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(
            f"[AI聊天] 用户: {request.user.username}, "\
            f"问题: {question[:50]}..., 模式: {mode}, RAG: {use_rag}, "\
            f"对话ID: {conversation_id}, 文档数: {len(document_ids)}"
        )
        
        # ==========================
        # 🆕 Orchestrator集成
        # ==========================
        # 检测是否应该使用Orchestrator执行工作流
        from apps.ai.orchestrator import get_orchestrator, WorkflowConfigLoader, ExecutionContext
        from apps.ai.models import AIDocument
        import uuid
        
        # 1. 识别意图
        recognizer = get_intent_recognizer()
        intent = recognizer.recognize(question, mode)
        function_id = intent.function_id
        
        # 2. 检查是否有文件上传
        uploaded_documents = []
        if document_ids:
            uploaded_documents = list(AIDocument.objects.filter(
                id__in=document_ids,
                uploaded_by=request.user
            ))
            logger.info(f"[Orchestrator] 找到 {len(uploaded_documents)} 个上传文档")
        
        # 3. 查找匹配的工作流配置
        workflow_config = WorkflowConfigLoader.find_matching_workflow(
            function_id=function_id,
            has_file_upload=bool(uploaded_documents)
        )
        
        # 4. 如果找到工作流，使用Orchestrator执行
        if workflow_config:
            logger.info(f"[Orchestrator] 触发工作流: {workflow_config.name}")
            
            # 创建执行上下文
            workflow_id = str(uuid.uuid4())
            execution_context = ExecutionContext(
                user=request.user,
                workflow_id=workflow_id,
                initial_input=question,
                uploaded_files=uploaded_documents,
                variables={
                    "conversation_id": conversation_id,
                    "mode": mode,
                    "use_rag": use_rag,
                    "request_data": dict(data),
                },
            )
            
            # 获取Orchestrator实例并执行工作流
            orchestrator = get_orchestrator()
            
            # 记录路由决策
            AIRoutingLog.objects.create(
                user=request.user,
                query=question,
                recognized_function=intent.function_id,
                confidence=intent.confidence,
                method=intent.method,
                reasoning=intent.reasoning,
                manual_mode=mode if mode else "",
            )

            def generate_workflow():
                try:
                    for progress in orchestrator.execute_workflow(
                        workflow_config, execution_context, yield_progress=True
                    ):
                        yield f"data: {json.dumps(progress, ensure_ascii=False)}\n\n"

                    final_result = {
                        "type": "final_result",
                        "workflow_id": workflow_id,
                        "results": {},
                    }
                    for step_result in execution_context.step_results.values():
                        if step_result.success and "answer" in step_result.data:
                            final_result["results"]["answer"] = step_result.data["answer"]
                            break
                    yield f"data: {json.dumps(final_result, ensure_ascii=False)}\n\n"
                    yield "data: [DONE]\n\n"
                except Exception as exc:
                    logger.error("[Orchestrator] 工作流执行失败: %s", exc, exc_info=True)
                    yield f"data: {json.dumps({'type': 'error', 'message': str(exc)}, ensure_ascii=False)}\n\n"

            response = StreamingHttpResponse(generate_workflow(), content_type="text/event-stream")
            response["Cache-Control"] = "no-cache"
            response["X-Accel-Buffering"] = "no"
            return response
        
        # 如果没有匹配的工作流，则继续执行原有的AI聊天逻辑
        logger.info(f"[Orchestrator] 未匹配到工作流，继续执行标准AI聊天逻辑")
        
        # ⚠️ 已废弃，保留仅为向后兼容，优先使用智能意图识别
        # conversation_id = request.data.get('conversation_id')  # ✅ 接收对话ID
        # document_ids = request.data.get('document_ids', [])  # ✅ 接收文档ID列表
        
        # if not question or not question.strip():
        #     return Response(
        #         {'error': '问题不能为空'},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        
        # ✅ 读取上传的文档内容
        uploaded_documents_context = ""
        if document_ids:
            logger.info(f"[文档上下文] 收到 {len(document_ids)} 个文档ID: {document_ids}")
            try:
                # from .models import AIDocument # Already imported by Orchestrator integration
                # 安全检查：只能访问当前用户上传的文档
                docs = AIDocument.objects.filter(
                    id__in=document_ids,
                    uploaded_by=request.user  # ✅ 正确字段
                )
                logger.info(f"[文档上下文] 找到 {docs.count()} 个有效文档")
                
                if docs.count() == 0:
                    logger.warning(f"[文档上下文] ⚠️ 没有找到任何文档！用户ID: {request.user.id}, 文档IDs: {document_ids}")
                
                for doc in docs:
                    # ✅ 检查content是否为空
                    if not doc.content or doc.content.strip() == "":
                        logger.error(f"[文档上下文] ❌ 文档 {doc.id} 的content为空！文件: {doc.title}")
                        logger.error(f"[文档上下文] metadata: {doc.metadata}")
                        uploaded_documents_context += f"\n\n【文档: {doc.title}】\n[错误：文件内容为空，文件解析可能失败]\n"
                        continue
                    
                    # 截取前5000字符（避免token超限）
                    text_preview = doc.content[:5000] if len(doc.content) > 5000 else doc.content  # ✅ 使用content字段
                    uploaded_documents_context += f"\n\n【参考文档: {doc.title}】\n{text_preview}\n"
                    if len(doc.content) > 5000:
                        uploaded_documents_context += "\n(文档内容已截断，仅显示前5000字符)\n"
                    
                    logger.info(f"[文档上下文] ✅ 加载文档 {doc.id} 成功，长度: {len(doc.content)} 字符")
                
                logger.info(f"[文档上下文] 加载完成，总长度: {len(uploaded_documents_context)} 字符")
            except Exception as e:
                logger.error(f"[文档上下文] 加载失败: {e}", exc_info=True)
        
        # 🆕 内容安全审核
        moderator = get_content_moderator()
        moderation_result = moderator.moderate_input(question)
        if not moderation_result['safe']:
            logger.warning(
                f"[安全审核] 用户 {request.user.username} 的输入被拦截: "
                f"{', '.join(moderation_result['reasons'])}"
            )
            return Response(
                {
                    'error': '您的输入包含不当内容，请修改后重试',
                    'reasons': moderation_result['reasons']
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ========== 智能意图识别 ==========
        recognizer = get_intent_recognizer()
        intent_result = recognizer.recognize(query=question, mode=mode)
        
        # 记录路由决策（用于后续优化）
        AIRoutingLog.objects.create(
            user=request.user,
            query=question,
            recognized_function=intent_result.function_id,
            confidence=intent_result.confidence,
            method=intent_result.method,
            reasoning=intent_result.reasoning,
            manual_mode=mode if mode else "",
        )
        
        routed_function_id = intent_result.function_id
        logger.info(
            f"[意图识别] 用户={request.user.username}, 查询='{question[:50]}...', "
            f"识别={routed_function_id}, 置信度={intent_result.confidence:.2f}, 方法={intent_result.method}"
        )
        
        # ========== 创建或加载对话记录 ==========
        conversation = None
        conversation_history_messages = []  # ✅ 用于存储历史消息
        
        if conversation_id:
            # ✅ 如果提供了conversation_id，尝试加载现有对话
            try:
                conversation = AIConversation.objects.get(
                    id=conversation_id,
                    user=request.user
                )
                logger.info(f"[对话管理] 加载现有对话: {conversation.id}, 标题: {conversation.title}")
                
                # ✅ 加载历史消息（最近10条）
                history_messages = AIMessage.objects.filter(
                    conversation=conversation
                ).order_by('created_at')[:10]
                
                for msg in history_messages:
                    conversation_history_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
                
                logger.info(f"[多轮对话] 加载了 {len(conversation_history_messages)} 条历史消息")
            except AIConversation.DoesNotExist:
                logger.warning(f"[对话管理] 对话 {conversation_id} 不存在或无权访问")
                conversation_id = None  # 强制创建新对话
        
        if not conversation:
            # ✅ 创建新对话
            conversation_title = question[:47] + "..." if len(question) > 50 else question
            conversation = AIConversation.objects.create(
                user=request.user,
                title=conversation_title,
                ai_function=routed_function_id,
            )
            logger.info(f"[对话管理] 创建新对话: {conversation.id}, 标题: {conversation_title}")
        
        # 加载功能配置
        func_config = get_function_config(routed_function_id)
        use_rag = func_config.get("enable_rag", False)
        
        # 允许请求覆盖RAG设置（用于测试）
        if "use_rag" in request.data:
            use_rag = request.data.get("use_rag")
        
        # 初始化AI客户端
        try:
            ai_client = get_ai_client()
            logger.info(f"[AI客户端] 使用模型: {ai_client.get_model_name()}")
        except Exception as e:
            logger.error(f"[AI客户端] 初始化失败: {e}", exc_info=True)
            return Response(
                {'error': 'AI服务暂时不可用'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # 加载system prompt
        base_system_prompt = get_system_prompt(func_config.get("system_prompt_file", "prompts/generic.txt"))
        enhanced_system = base_system_prompt
        
        # RAG 逻辑
        if use_rag:
            try:
                rag_start = time.time()
                rag_engine = RAGEngine()
                
                # 格式化查询（如果有模板）
                query_template = func_config.get("rag_query_template", "{query}")
                rag_query = query_template.format(query=question)
                
                docs = rag_engine.retrieve(
                    query=rag_query,
                    top_k=5,
                    filters=func_config.get("rag_filters"),
                )
                rag_elapsed_ms = int((time.time() - rag_start) * 1000)
                logger.info(f"[RAG] 检索耗时: {rag_elapsed_ms}ms")
                
                if docs:
                    context_parts = []
                    for i, doc in enumerate(docs, 1):
                        source = doc.metadata.get("title", "未知来源")
                        similarity = doc.metadata.get("similarity", 0)
                        context_parts.append(
                            f"【参考资料 {i}】(相关度: {similarity:.2f})\\n"
                            f"来源：{source}\\n"
                            f"内容：{doc.page_content}\\n"
                        )
                    
                    context = "\\n".join(context_parts)
                    enhanced_system = f"""{base_system_prompt}

请基于以下参考资料回答用户问题，但请灵活运用：
- 优先使用参考资料中的准确信息
- 如果资料只提供部分线索，可结合你的知识进行合理推理和扩展
- 保持回答的自然和完整，不要生硬地引用资料
- 如果资料与问题完全无关，基于你的通用知识回答

{context}
"""
                    logger.info(f"[RAG] 检索成功：找到 {len(docs)} 条高质量文档")
                else:
                    logger.warning(f"[RAG] 未找到高质量文档，降级为通用模式")
            except Exception as e:
                logger.error(f"[RAG] 引擎异常: {e}，降级为通用模式", exc_info=True)
        else:
            logger.info(f"[AI] 使用标准对话模式（未启用 RAG）")
        
        # 🆕 搜索增强逻辑
        search_service = get_search_service()
        if search_service.should_search(question):
            try:
                logger.info(f"[搜索] 触发搜索增强模式")
                search_results = search_service.search(question, max_results=5)
                if search_results:
                    search_context = search_service.format_search_results(search_results)
                    enhanced_system = f"""{enhanced_system}

{search_context}
"""
                    logger.info(f"[搜索] 成功获取 {len(search_results)} 条搜索结果")
            except Exception as e:
                logger.warning(f"[搜索] 搜索失败: {e}")
        
        # ✅ 增强文档注入 - 将上传文档内容添加到system prompt
        if uploaded_documents_context:
            enhanced_system += f"\n\n⚠️ **重要提示**：用户上传了文件，请仔细阅读以下文件内容并基于文件内容回答问题：\n{uploaded_documents_context}\n"
            logger.info(f"[文档注入] 已将 {len(document_ids)} 个文档注入到系统提示中（总长度: {len(uploaded_documents_context)} 字符）")
        
        # 流式生成
        def generate():
            try:
                start_time = time.time()
                
                # ✅ 构建完整的消息列表
                messages = [
                    {"role": "system", "content": enhanced_system}
                ]
                
                # ✅ 添加历史消息（多轮对话）
                messages.extend(conversation_history_messages)
                
                # ✅ 构建当前用户问题（包含文档内容）
                current_question = question
                if uploaded_documents_context:
                    current_question = f"{question}\n\n{uploaded_documents_context}"
                    logger.info(f"[文档上下文] 已将文档内容注入到用户消息中")
                
                messages.append({"role": "user", "content": current_question})
                
                logger.info(f"[消息构建] 总消息数: {len(messages)} (system: 1, history: {len(conversation_history_messages)}, current: 1)")
                
                # 发送路由元数据（首个消息）+ 对话ID
                yield f"data: {json.dumps({'type': 'metadata', 'routed_to': routed_function_id, 'confidence': intent_result.confidence, 'method': intent_result.method, 'conversation_id': conversation.id})}\n\n"
                
                # 保存用户消息到数据库
                AIMessage.objects.create(
                    conversation=conversation,
                    role="user",
                    content=question,  # ✅ 保存原始问题（不含文档内容，避免重复）
                    model_used=ai_client.get_model_name(),
                )
                
                chunk_count = 0
                accumulated_answer = ""
                for chunk in ai_client.chat_completion_stream(messages=messages):
                    if chunk:
                        chunk_count += 1
                        accumulated_answer += chunk
                        yield f"data: {json.dumps({'type': 'text', 'content': chunk})}\n\n"
                
                # 🆕 审核AI输出
                output_moderation = moderator.moderate_output(accumulated_answer)
                if not output_moderation['safe']:
                    logger.warning(f"[安全审核] AI输出被拦截: {', '.join(output_moderation['reasons'])}")
                    accumulated_answer = "抱歉，AI生成的内容不符合安全规范，请换个问题试试。"
                
                # 保存AI回答到数据库
                AIMessage.objects.create(
                    conversation=conversation,
                    role="assistant",
                    content=accumulated_answer,
                    model_used=ai_client.get_model_name(),
                )
                
                elapsed_ms = int((time.time() - start_time) * 1000)
                yield f"data: {json.dumps({'type': 'done', 'elapsed_ms': elapsed_ms, 'chunks': chunk_count, 'conversation_id': conversation.id})}\n\n"
                
                logger.info(f"[AI生成] 完成: {chunk_count}个片段, 耗时: {elapsed_ms}ms, 对话ID: {conversation.id}")
                
            except Exception as e:
                logger.error(f"[流式生成] 失败: {e}", exc_info=True)
                yield f"data: {json.dumps({'type': 'error', 'message': 'AI生成失败'})}\n\n"
        
        response = StreamingHttpResponse(generate(), content_type="text/event-stream")
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response
        
    except Exception as e:
        logger.error(f"[流式聊天] 请求处理失败: {e}", exc_info=True)
        return Response({'error': '服务器内部错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_chat_sync(request):
    """
    同步AI聊天API (支持智能意图识别 + RAG)
    
    Request body:
    {
        "question": "用户的问题",
        "mode": "course_query",  # 可选
        "use_rag": true/false     # 可选
    }
    
    Response:
    {
        "answer": "AI的回答",
        "routed_to": "course_query",
        "confidence": 0.95,
        "method": "keyword",
        "elapsed_ms": 325,
        "used_rag": true,
        "model": "llama-3.3-70b-versatile"
    }
    """
    
    try:
        question = request.data.get('question')
        mode = request.data.get('mode')
        
        if not question or not question.strip():
            return Response(
                {'error': '问题不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ========== 智能意图识别 ==========
        recognizer = get_intent_recognizer()
        intent_result = recognizer.recognize(query=question, mode=mode)
        
        # 记录路由决策
        AIRoutingLog.objects.create(
            user=request.user,
            query=question,
            recognized_function=intent_result.function_id,
            confidence=intent_result.confidence,
            method=intent_result.method,
            reasoning=intent_result.reasoning,
            manual_mode=mode if mode else "",
        )
        
        routed_function_id = intent_result.function_id
        logger.info(
            f"[同步聊天] 用户={request.user.username}, 识别={routed_function_id}, "
            f"置信度={intent_result.confidence:.2f}"
        )
        
        # 加载功能配置
        func_config = get_function_config(routed_function_id)
        use_rag = func_config.get("enable_rag", False)
        
        if "use_rag" in request.data:
            use_rag = request.data.get("use_rag")
        
        # 初始化AI客户端
        try:
            ai_client = get_ai_client()
        except Exception as e:
            logger.error(f"[AI客户端] 初始化失败: {e}", exc_info=True)
            return Response(
                {'error': 'AI服务暂时不可用'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        start_time = time.time()
        used_rag = False
        
        # 加载system prompt
        base_system_prompt = get_system_prompt(func_config.get("system_prompt_file", "prompts/generic.txt"))
        enhanced_system = base_system_prompt
        
        # RAG 逻辑
        if use_rag:
            try:
                rag_engine = RAGEngine()
                query_template = func_config.get("rag_query_template", "{query}")
                rag_query = query_template.format(query=question)
                docs = rag_engine.retrieve(
                    query=rag_query,
                    top_k=5,
                    filters=func_config.get("rag_filters"),
                )
                
                if docs:
                    context_parts = []
                    for i, doc in enumerate(docs, 1):
                        source = doc.metadata.get("title", "未知来源")
                        similarity = doc.metadata.get("similarity", 0)
                        context_parts.append(
                            f"【参考资料 {i}】(相关度: {similarity:.2f})\\n"
                            f"来源：{source}\\n"
                            f"内容：{doc.page_content}\\n"
                        )
                    
                    context = "\\n".join(context_parts)
                    enhanced_system = f"""{base_system_prompt}

请基于以下参考资料回答用户问题，但请灵活运用：
- 优先使用参考资料中的准确信息
- 如果资料只提供部分线索，可结合你的知识进行合理推理和扩展
- 保持回答的自然和完整，不要生硬地引用资料
- 如果资料与问题完全无关，基于你的通用知识回答

{context}
"""
                    used_rag = True
                    logger.info(f"[RAG] 检索成功：找到 {len(docs)} 条高质量文档")
                else:
                    logger.warning(f"[RAG] 未找到高质量文档，降级为通用模式")
            except Exception as e:
                logger.error(f"[RAG] 引擎异常: {e}，降级为通用模式", exc_info=True)
        else:
            logger.info(f"[AI] 使用标准对话模式（未启用 RAG）")
        
        # 构建消息并生成回答
        messages = [
            {"role": "system", "content": enhanced_system},
            {"role": "user", "content": question},
        ]
        
        try:
            answer = ai_client.chat_completion(messages=messages)
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            logger.info(f"[同步聊天] 成功: 耗时={elapsed_ms}ms, RAG={used_rag}")
            
            return Response({
                "answer": answer,
                "routed_to": routed_function_id,
                "confidence": intent_result.confidence,
                "method": intent_result.method,
                "elapsed_ms": elapsed_ms,
                "used_rag": used_rag,
                "model": ai_client.get_model_name(),
            })
            
        except Exception as e:
            logger.error(f"[AI生成] 失败: {e}", exc_info=True)
            return Response({'error': 'AI生成失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        logger.error(f"[同步聊天] 未预期的错误: {e}", exc_info=True)
        return Response({'error': '服务器内部错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_health(request):
    """AI服务健康检查"""
    
    services = {
        "ai_client": {"available": False, "model": None},
    }
    
    try:
        client = get_ai_client()
        available = client.check_health()
        services["ai_client"] = {
            "available": bool(available),
            "model": client.get_model_name(),
        }
    except Exception as e:
        logger.error(f"[健康检查] AI客户端异常: {e}")
    
    status_value = "healthy" if services["ai_client"]["available"] else "unhealthy"
    
    return Response({
        "status": status_value,
        "services": services,
    })


# ========== Phase 2: 多轮对话管理 API ==========

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_conversation_create(request):
    """
    创建新的对话会话
    
    Request body:
    {
        "title": "我的对话",  # 可选
        "ai_function": "general_chat"  # 可选，默认 general_chat
    }
    
    Response:
    {
        "conversation_id": 123,
        "title": "我的对话",
        "ai_function": "general_chat",
        "created_at": "2025-11-30T12:34:56Z"
    }
    """
    try:
        title = request.data.get('title', '新对话')
        ai_function = request.data.get('ai_function', 'general_chat')
        
        conversation = AIConversation.objects.create(
            user=request.user,
            title=title,
            ai_function=ai_function,
        )
        
        logger.info(f"[对话管理] 用户 {request.user.username} 创建新对话: {conversation.id}")
        
        return Response({
            "conversation_id": conversation.id,
            "title": conversation.title,
            "ai_function": conversation.ai_function,
            "created_at": conversation.created_at.isoformat(),
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"[对话管理] 创建对话失败: {e}", exc_info=True)
        return Response({'error': '创建对话失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_conversation_chat(request, conversation_id):
    """
    在现有对话中发送消息（支持多轮上下文）
    
    URL: /api/ai/conversations/<conversation_id>/chat/
    
    Request body:
    {
        "question": "用户的问题",
        "mode": "course_query",  # 可选
        "use_rag": true/false,   # 可选
        "max_context_tokens": 2000  # 可选，上下文Token限制
    }
    
    Response:
    {
        "answer": "AI的回答",
        "routed_to": "course_query",
        "confidence": 0.95,
        "method": "keyword",
        "conversation_id": 123,
        "message_id": 456,
        "context_messages_count": 5,
        "elapsed_ms": 325
    }
    """
    try:
        question = request.data.get('question')
        mode = request.data.get('mode')
        max_context_tokens = request.data.get('max_context_tokens', 2000)
        
        if not question or not question.strip():
            return Response(
                {'error': '问题不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 验证对话是否存在且属于当前用户
        try:
            conversation = AIConversation.objects.get(id=conversation_id, user=request.user)
        except AIConversation.DoesNotExist:
            return Response(
                {'error': '对话不存在或无权访问'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # ========== 智能意图识别 ==========
        recognizer = get_intent_recognizer()
        intent_result = recognizer.recognize(query=question, mode=mode)
        
        # 记录路由决策
        AIRoutingLog.objects.create(
            user=request.user,
            query=question,
            recognized_function=intent_result.function_id,
            confidence=intent_result.confidence,
            method=intent_result.method,
            reasoning=intent_result.reasoning,
            manual_mode=mode if mode else "",
        )
        
        routed_function_id = intent_result.function_id
        logger.info(
            f"[多轮对话] 对话={conversation_id}, 识别={routed_function_id}, "
            f"置信度={intent_result.confidence:.2f}"
        )
        
        # 加载功能配置
        func_config = get_function_config(routed_function_id)
        use_rag = func_config.get("enable_rag", False)
        
        if "use_rag" in request.data:
            use_rag = request.data.get("use_rag")
        
        # 初始化AI客户端
        try:
            ai_client = get_ai_client()
        except Exception as e:
            logger.error(f"[AI客户端] 初始化失败: {e}", exc_info=True)
            return Response(
                {'error': 'AI服务暂时不可用'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        start_time = time.time()
        
        # ========== 使用 Context Manager 获取历史上下文 ==========
        context_manager = get_context_manager()
        
        # 获取历史消息
        history_messages = context_manager.get_context_messages(
            conversation_id=conversation_id,
            max_tokens=max_context_tokens,
            include_system=False
        )
        
        logger.info(
            f"[多轮对话] 对话={conversation_id} 加载了 {len(history_messages)} 条历史消息"
        )
        
        # 加载system prompt
        base_system_prompt = get_system_prompt(func_config.get("system_prompt_file", "prompts/generic.txt"))
        enhanced_system = base_system_prompt
        
        # RAG 逻辑
        used_rag = False
        if use_rag:
            try:
                rag_engine = RAGEngine()
                query_template = func_config.get("rag_query_template", "{query}")
                rag_query = query_template.format(query=question)
                docs = rag_engine.retrieve(
                    query=rag_query,
                    top_k=5,
                    filters=func_config.get("rag_filters"),
                )
                
                if docs:
                    context_parts = []
                    for i, doc in enumerate(docs, 1):
                        source = doc.metadata.get("title", "未知来源")
                        similarity = doc.metadata.get("similarity", 0)
                        context_parts.append(
                            f"【参考资料 {i}】(相关度: {similarity:.2f})\\n"
                            f"来源：{source}\\n"
                            f"内容：{doc.page_content}\\n"
                        )
                    
                    context = "\\n".join(context_parts)
                    enhanced_system = f"""{base_system_prompt}

请基于以下参考资料回答用户问题，但请灵活运用：
- 优先使用参考资料中的准确信息
- 如果资料只提供部分线索，可结合你的知识进行合理推理和扩展
- 保持回答的自然和完整，不要生硬地引用资料
- 如果资料与问题完全无关，基于你的通用知识回答

{context}
"""
                    used_rag = True
                    logger.info(f"[RAG] 检索成功：找到 {len(docs)} 条高质量文档")
            except Exception as e:
                logger.error(f"[RAG] 引擎异常: {e}，降级为通用模式", exc_info=True)
        
        # 构建完整的消息列表：system + 历史消息 + 当前问题
        messages = [{"role": "system", "content": enhanced_system}]
        messages.extend(history_messages)
        messages.append({"role": "user", "content": question})
        
        # 生成回答
        try:
            answer = ai_client.chat_completion(messages=messages)
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            # ========== 保存用户问题和AI回答到数据库 ==========
            user_message = context_manager.add_message(
                conversation_id=conversation_id,
                role="user",
                content=question,
                model_used=ai_client.get_model_name()
            )
            
            assistant_message = context_manager.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=answer,
                model_used=ai_client.get_model_name()
            )
            
            logger.info(
                f"[多轮对话] 成功: 对话={conversation_id}, "
                f"耗时={elapsed_ms}ms, RAG={used_rag}, 上下文={len(history_messages)}条"
            )
            
            return Response({
                "answer": answer,
                "routed_to": routed_function_id,
                "confidence": intent_result.confidence,
                "method": intent_result.method,
                "conversation_id": conversation_id,
                "message_id": assistant_message.id if assistant_message else None,
                "context_messages_count": len(history_messages),
                "elapsed_ms": elapsed_ms,
                "used_rag": used_rag,
                "model": ai_client.get_model_name(),
            })
            
        except Exception as e:
            logger.error(f"[AI生成] 失败: {e}", exc_info=True)
            return Response({'error': 'AI生成失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        logger.error(f"[多轮对话] 未预期的错误: {e}", exc_info=True)
        return Response({'error': '服务器内部错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def ai_conversation_list(request):
    """
    获取用户的对话列表
    
    Response:
    {
        "conversations": [
            {
                "id": 123,
                "title": "我的对话",
                "ai_function": "general_chat",
                "message_count": 10,
                "total_tokens": 1500,
                "created_at": "2025-11-30T12:34:56Z",
                "updated_at": "2025-11-30T13:45:00Z"
            }
        ]
    }
    """
    try:
        if request.method == 'POST':
            title = request.data.get('title', '新对话')
            ai_function = request.data.get('ai_function', 'general')
            conversation = AIConversation.objects.create(
                user=request.user,
                title=title,
                ai_function=ai_function,
            )
            return Response({
                "id": conversation.id,
                "user": conversation.user_id,
                "title": conversation.title,
                "ai_function": conversation.ai_function,
                "message_count": 0,
                "total_tokens": conversation.total_tokens,
                "created_at": conversation.created_at.isoformat(),
                "updated_at": conversation.updated_at.isoformat(),
            }, status=status.HTTP_201_CREATED)

        conversations = (
            AIConversation.objects.filter(user=request.user)
            .annotate(message_count=Count('messages'))
            .order_by('-updated_at')
        )
        
        result = []
        for conv in conversations:
            result.append({
                "id": conv.id,
                "user": conv.user_id,
                "title": conv.title,
                "ai_function": conv.ai_function,
                "message_count": conv.message_count,
                "total_tokens": conv.total_tokens,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
            })
        
        logger.info(f"[对话管理] 用户 {request.user.username} 获取对话列表: {len(result)}个对话")
        
        return Response({"conversations": result, "total": len(result)})
        
    except Exception as e:
        logger.error(f"[对话管理] 获取对话列表失败: {e}", exc_info=True)
        return Response({'error': '获取对话列表失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def ai_conversation_detail(request, conversation_id):
    """
    获取对话详情（GET）或删除对话（DELETE）
    
    GET Response:
    {
        "conversation": {...},
        "messages": [...]
    }
    
    DELETE Response:
    {
        "message": "对话已删除"
    }
    """
    try:
        # 验证对话是否存在且属于当前用户
        try:
            conversation = AIConversation.objects.get(id=conversation_id, user=request.user)
        except AIConversation.DoesNotExist:
            return Response(
                {'error': '对话不存在或无权访问'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # DELETE: 删除对话
        if request.method == 'DELETE':
            conversation_title = conversation.title
            conversation.delete()
            logger.info(f"[对话管理] 用户 {request.user.username} 删除对话: {conversation_id} ({conversation_title})")
            return Response({
                "message": "对话已删除"
            })
        
        # GET: 获取对话详情
        # 获取所有消息
        messages = AIMessage.objects.filter(conversation=conversation).order_by('created_at')
        
        message_list = []
        for msg in messages:
            message_list.append({
                'id': msg.id,
                'role': msg.role,
                'content': msg.content,
                'tokens': msg.tokens,
                'model_used': msg.model_used,
                'created_at': msg.created_at.isoformat(),
            })
        
        logger.info(f"[对话管理] 用户 {request.user.username} 获取对话详情: {conversation_id}")
        
        return Response({
            "conversation": {
                "id": conversation.id,
                "title": conversation.title,
                "ai_function": conversation.ai_function,
                "total_tokens": conversation.total_tokens,
                "created_at": conversation.created_at.isoformat(),
                "updated_at": conversation.updated_at.isoformat(),
            },
            "messages": message_list,
        })
        
    except Exception as e:
        logger.error(f"[对话管理] 操作失败: {e}", exc_info=True)
        return Response({'error': '服务器内部错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_conversation_messages(request, conversation_id):
    """
    获取对话的所有历史消息（轻量级端点，用于前端加载历史）
    
    Response:
    {
        "conversation_id": 123,
        "messages": [
            {
                "id": 456,
                "role": "user",
                "content": "你好",
                "created_at": "2025-11-30T12:34:56Z"
            },
            {
                "id": 457,
                "role": "assistant",
                "content": "你好！有什么可以帮你的吗？",
                "created_at": "2025-11-30T12:34:58Z"
            }
        ]
    }
    """
    try:
        # 验证对话是否存在且属于当前用户
        try:
            conversation = AIConversation.objects.get(
                id=conversation_id,
                user=request.user
            )
        except AIConversation.DoesNotExist:
            return Response(
                {'error': '对话不存在或无权访问'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 获取所有消息，按时间排序
        messages = AIMessage.objects.filter(
            conversation=conversation
        ).order_by('created_at')
        
        logger.info(
            f"[对话消息] 用户 {request.user.username} 获取对话 {conversation_id} "
            f"的历史消息，共 {messages.count()} 条"
        )
        
        return Response({
            'conversation_id': conversation_id,
            'messages': [
                {
                    'id': msg.id,
                    'role': msg.role,
                    'content': msg.content,
                    'created_at': msg.created_at.isoformat()
                }
                for msg in messages
            ]
        })
        
    except Exception as e:
        logger.error(f"[对话消息] 获取失败: {e}", exc_info=True)
        return Response(
            {'error': '服务器错误'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ========== Phase 4: API 增强 ==========

@api_view(['GET'])
def ai_functions_list(request):
    """
    获取所有 AI 功能列表（无需认证，供前端展示）
    
    Response:
    {
        "functions": [
            {
                "id": "course_query",
                "name": "课程查询",
                "category": "academic",
                "description": "查询APU课程信息",
                "enable_rag": true,
                "keywords": ["课程", "选课", "学分"],
                "examples": ["APU有什么计算机课程？"]
            }
        ]
    }
    """
    try:
        config = load_functions_config()
        functions = config.get('functions', [])
        
        # 格式化输出
        result = []
        for func in functions:
            result.append({
                "id": func.get('id'),
                "name": func.get('name'),
                "category": func.get('category'),
                "description": func.get('description', ''),
                "enable_rag": func.get('enable_rag', False),
                "keywords": func.get('keywords', []),
                "examples": func.get('examples', []),
            })
        
        logger.info(f"[API增强] 返回 {len(result)} 个 AI 功能")
        
        return Response({"functions": result})
        
    except Exception as e:
        logger.error(f"[API增强] 获取功能列表失败: {e}", exc_info=True)
        return Response({'error': '获取功能列表失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_intent_test(request):
    """
    测试意图识别（供开发/调试使用）
    
    Request body:
    {
        "query": "APU有什么课程？",
        "mode": "course_query"  # 可选，用于对比
    }
    
    Response:
    {
        "query": "APU有什么课程？",
        "result": {
            "function_id": "course_query",
            "confidence": 0.85,
            "method": "keyword",
            "reasoning": "匹配关键词: 课程"
        },
        "all_scores": {
            "course_query": 0.85,
            "academic_qa": 0.45,
            ...
        }
    }
    """
    try:
        query = request.data.get('query')
        mode = request.data.get('mode')
        
        if not query:
            return Response(
                {'error': '查询不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 执行意图识别
        recognizer = get_intent_recognizer()
        intent_result = recognizer.recognize(query=query, mode=mode)
        
        # 获取所有功能的得分（用于调试）
        all_scores = {}
        config = load_functions_config()
        for func in config.get('functions', []):
            func_id = func['id']
            # 简单的关键词匹配得分
            keywords = func.get('keywords', [])
            score = sum(1 for kw in keywords if kw.lower() in query.lower()) / max(len(keywords), 1)
            all_scores[func_id] = round(score, 2)
        
        logger.info(f"[意图测试] 查询='{query}', 识别={intent_result.function_id}")
        
        return Response({
            "query": query,
            "result": {
                "function_id": intent_result.function_id,
                "confidence": intent_result.confidence,
                "method": intent_result.method,
                "reasoning": intent_result.reasoning,
            },
            "all_scores": all_scores,
        })
        
    except Exception as e:
        logger.error(f"[意图测试] 失败: {e}", exc_info=True)
        return Response({'error': '意图识别失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def ai_prompts_list(request):
    """
    获取所有可用的 Prompt 列表（供调试）
    
    Response:
    {
        "prompts": [
            {
                "file": "course_query.txt",
                "variables": ["user_name", "university"],
                "size": 1234
            }
        ],
        "total": 21
    }
    """
    try:
        prompt_manager = get_prompt_manager()
        
        # 验证所有 Prompts
        validation_result = prompt_manager.validate_prompts()
        
        logger.info(f"[Prompt列表] 总计: {validation_result['total']}, 成功: {validation_result['success']}")
        
        return Response({
            "prompts": validation_result['details'],
            "total": validation_result['total'],
            "success": validation_result['success'],
            "failed": validation_result['failed'],
        })
        
    except Exception as e:
        logger.error(f"[Prompt列表] 失败: {e}", exc_info=True)
        return Response({'error': '获取Prompt列表失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
