"""
AI视图 - 提供AI聊天和RAG查询功能
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import StreamingHttpResponse
import json
import logging
import time

from .services.groq_client import GroqClient
from .services.ollama_client import OllamaClient
from .services.rag_engine import RAGEngine

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_chat_stream(request):
    """
    流式AI聊天API
    
    Request body:
    {
        "question": "用户的问题",
        "use_rag": true/false,  # 是否使用RAG检索
        "category": "academic"  # AI类别（预留）
    }
    
    Response: Server-Sent Events (SSE) stream
    """
    
    try:
        # 获取请求参数
        question = request.data.get('question')
        use_rag = request.data.get('use_rag', True)
        category = request.data.get('category', 'academic')
        
        # 验证参数
        if not question or not question.strip():
            return Response(
                {'error': '问题不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logger.info(f"AI聊天请求: question='{question[:50]}...', use_rag={use_rag}")
        
        # 初始化AI客户端（优先Groq）
        try:
            ai_client = GroqClient()
            logger.info("使用Groq客户端")
        except Exception as e:
            logger.warning(f"Groq初始化失败，回退到Ollama: {e}")
            try:
                ai_client = OllamaClient()
                logger.info("使用Ollama客户端")
            except Exception as e2:
                logger.error(f"AI客户端初始化失败: {e2}")
                return Response(
                    {'error': 'AI服务暂时不可用，请稍后重试'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
        
        # 流式生成函数
        def generate():
            try:
                start_time = time.time()
                
                # 如果使用RAG，先检索相关文档
                context = ""
                if use_rag:
                    try:
                        rag = RAGEngine()
                        docs = rag.retrieve(question, top_k=3)
                        
                        if docs:
                            context = "\n\n".join([
                                f"[文档{i+1}]: {doc.page_content}"
                                for i, doc in enumerate(docs)
                            ])
                            
                            # 发送检索到的文档数量
                            yield f"data: {json.dumps({'type': 'rag_docs', 'count': len(docs)})}\n\n"
                            
                            logger.info(f"RAG检索到 {len(docs)} 个相关文档")
                    except Exception as e:
                        logger.warning(f"RAG检索失败: {e}")
                        # RAG失败不影响对话，继续进行
                
                # 读取系统Prompt
                try:
                    from pathlib import Path
                    prompt_path = Path(__file__).parent / 'prompts' / 'academic.txt'
                    with open(prompt_path, 'r', encoding='utf-8') as f:
                        system_prompt = f.read()
                except Exception as e:
                    logger.warning(f"读取系统Prompt失败: {e}")
                    system_prompt = "你是UniPulse Asia的学业助手，专门帮助大学生解决学业相关问题。"
                
                # 构建消息
                if context:
                    # 有RAG上下文
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user",
                            "content": f"""基于以下知识库内容回答问题：

知识库内容：
{context}

用户问题：{question}

请根据知识库内容提供准确的答案。如果知识库中没有相关信息，请明确说明。"""
                        }
                    ]
                else:
                    # 普通对话
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": question}
                    ]
                
                # 流式生成回答
                for chunk in ai_client.stream_chat(messages):
                    yield f"data: {json.dumps({'type': 'text', 'content': chunk})}\n\n"
                
                # 发送完成信号
                elapsed_ms = int((time.time() - start_time) * 1000)
                yield f"data: {json.dumps({'type': 'done', 'elapsed_ms': elapsed_ms})}\n\n"
                
                logger.info(f"AI响应完成，耗时: {elapsed_ms}ms")
                
            except Exception as e:
                logger.error(f"流式生成失败: {e}", exc_info=True)
                yield f"data: {json.dumps({'type': 'error', 'message': '抱歉，生成回答时出错了'})}\n\n"
        
        # 返回SSE流
        response = StreamingHttpResponse(
            generate(),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        
        return response
        
    except Exception as e:
        logger.error(f"AI聊天请求处理失败: {e}", exc_info=True)
        return Response(
            {'error': '服务器内部错误'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_chat_sync(request):
    """
    同步AI聊天API（用于简单场景）
    
    Request body:
    {
        "question": "用户的问题",
        "use_rag": true/false
    }
    
    Response:
    {
        "answer": "AI的回答",
        "elapsed_ms": 325,
        "sources": [...]  # 如果使用RAG
    }
    """
    
    try:
        question = request.data.get('question')
        use_rag = request.data.get('use_rag', True)
        
        if not question or not question.strip():
            return Response(
                {'error': '问题不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 初始化AI客户端
        try:
            ai_client = GroqClient()
        except:
            ai_client = OllamaClient()
        
        # 如果使用RAG
        if use_rag:
            try:
                rag = RAGEngine()
                answer = rag.rag_query(question, ai_client, top_k=3)
                
                return Response({
                    'answer': answer,
                    'used_rag': True
                })
            except Exception as e:
                logger.error(f"RAG查询失败: {e}")
                # 回退到普通对话
                use_rag = False
        
        # 普通对话
        result = ai_client.chat([{"role": "user", "content": question}])
        
        return Response({
            'answer': result['content'],
            'elapsed_ms': result['elapsed_ms'],
            'used_rag': False
        })
        
    except Exception as e:
        logger.error(f"同步聊天失败: {e}", exc_info=True)
        return Response(
            {'error': '服务器内部错误'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_health(request):
    """
    健康检查API - 检查AI服务是否可用
    
    Response:
    {
        "status": "ok",
        "services": {
            "groq": true/false,
            "ollama": true/false,
            "rag": true/false
        }
    }
    """
    
    services_status = {
        "groq": False,
        "ollama": False,
        "rag": False
    }
    
    # 检查Groq
    try:
        GroqClient()
        services_status["groq"] = True
    except:
        pass
    
    # 检查Ollama
    try:
        OllamaClient()
        services_status["ollama"] = True
    except:
        pass
    
    # 检查RAG
    try:
        RAGEngine()
        services_status["rag"] = True
    except:
        pass
    
    overall_status = "ok" if any(services_status.values()) else "error"
    
    return Response({
        "status": overall_status,
        "services": services_status
    })