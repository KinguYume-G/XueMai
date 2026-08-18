"""
文件上传相关的API视图

提供以下端点：
- POST /api/ai/upload/ - 上传文件
- GET /api/ai/documents/ - 获取用户上传的文档列表
- DELETE /api/ai/documents/<document_id>/ - 删除文档
- POST /api/ai/documents/<document_id>/analyze/ - 分析文档内容
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import logging
import hashlib  # ✅ 添加缺失的import
from pathlib import Path

from .models import AIDocument
from .services.file_processor import FileProcessor
from .clients import get_ai_client
from .views import get_system_prompt

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_file(request):
    """
    上传文件
    
    Request:
        - file: 文件对象（multipart/form-data）
        - conversation_id: 可选，关联对话ID
        - description: 可选，文件描述
    
    Response:
    {
        "document_id": 123,
        "file_name": "resume.pdf",
        "file_type": "pdf",
        "file_size": 12345,
        "extracted_text": "...",
        "preview_url": "/media/uploads/..."
    }
    """
    try:
        # 获取上传的文件
        if 'file' not in request.FILES:
            return Response(
                {'error': '请选择要上传的文件'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file_obj = request.FILES['file']
        conversation_id = request.data.get('conversation_id')
        description = request.data.get('description', '')
        
        # 验证文件
        try:
            validation_result = FileProcessor.validate_file(file_obj)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file_ext = validation_result['file_extension']
        file_name = validation_result['file_name']
        
        # ✅ 核心修复：一次性读取文件字节，避免指针问题
        logger.info(f"[文件上传] 开始处理文件: {file_name}, 大小: {file_obj.size} bytes")
        file_obj.seek(0)
        file_bytes = file_obj.read()
        logger.info(f"[文件上传] 已读取文件字节: {len(file_bytes)} bytes")
        
        # 计算文件哈希（用于去重）
        file_hash = hashlib.md5(file_bytes).hexdigest()
        logger.info(f"[文件上传] 文件哈希: {file_hash}")
        
        # 检查是否已上传过相同文件
        existing_doc = AIDocument.objects.filter(
            uploaded_by=request.user,
            metadata__file_hash=file_hash
        ).first()
        
        if existing_doc:
            # ✅ 检查现有文件是否有效
            if existing_doc.content and existing_doc.content.strip():
                logger.info(f"[文件上传] 用户 {request.user.username} 上传了重复文件: {file_name}")
                return Response({
                    "document_id": existing_doc.id,
                    "file_name": existing_doc.title,
                    "file_type": existing_doc.doc_type,
                    "duplicate": True,
                    "message": "此文件已上传过",
                })
            else:
                # ⚠️ 现有文件内容为空（可能是之前处理失败），删除旧记录并重新处理
                logger.warning(f"[文件上传] 发现重复文件 {file_name} (ID: {existing_doc.id}) 但内容为空，将重新处理")
                existing_doc.delete()
        
        # ✅ 修复：从字节流处理文件
        logger.info(f"[文件处理] 开始处理文件内容，类型: {file_ext}")
        try:
            from io import BytesIO
            file_stream = BytesIO(file_bytes)
            processing_result = FileProcessor.process_file_from_stream(file_stream, file_ext)
            extracted_text = processing_result.get('extracted_text', '')
            file_metadata = processing_result.get('metadata', {})
            
            logger.info(f"[文件处理] ✅ 文件处理成功，提取文本长度: {len(extracted_text)} 字符")
            
            # ✅ 验证提取结果
            if not extracted_text or not extracted_text.strip():
                logger.error(f"[文件处理] ❌ 提取内容为空！文件可能损坏或格式不支持")
                logger.error(f"[文件处理] 文件元数据: {file_metadata}")
                logger.error(f"[文件处理] 处理结果: {processing_result}")
                # 不直接返回错误，而是继续保存并标记错误
                file_metadata['processing_warning'] = "文件内容提取为空"
                
        except Exception as e:
            logger.error(f"[文件处理] ❌ 文件处理失败: {e}", exc_info=True)
            extracted_text = ""
            file_metadata = {"processing_error": str(e)}
            # ❌ 不再静默失败，而是返回明确的错误
            return Response({
                'error': '文件处理失败',
                'details': '请检查文件格式是否正确，或联系管理员'
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        
        # 保存文件到磁盘
        upload_dir = f"uploads/{request.user.id}/"
        if conversation_id:
            upload_dir += f"{conversation_id}/"
        
        # 生成唯一文件名
        safe_filename = f"{file_hash[:8]}_{file_name}"
        file_path = os.path.join(upload_dir, safe_filename)
        
        # ✅ 使用 BytesIO 保存文件
        from io import BytesIO
        save_stream = BytesIO(file_bytes)
        saved_path = default_storage.save(file_path, ContentFile(save_stream.read()))
        
        logger.info(f"[文件上传] 文件已保存到: {saved_path}")
        
        # 保存到数据库
        document = AIDocument.objects.create(
            doc_type="other",  # 可以根据文件类型细化
            title=file_name,
            content=extracted_text,
            uploaded_by=request.user,
            metadata={
                "file_hash": file_hash,
                "file_size": file_obj.size,
                "file_extension": file_ext,
                "file_path": saved_path,
                "conversation_id": conversation_id,
                "description": description,
                **file_metadata,
            },
        )
        
        logger.info(
            f"[文件上传] 用户 {request.user.username} 上传文件成功: {file_name}, "
            f"文档ID: {document.id}, 提取文本长度: {len(extracted_text)}"
        )
        
        return Response({
            "document_id": document.id,
            "file_name": file_name,
            "file_type": file_ext,
            "file_size": file_obj.size,
            "extracted_text_length": len(extracted_text),
            "extracted_text_preview": extracted_text[:500] if extracted_text else "",
            "preview_url": default_storage.url(saved_path),
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"[文件上传] 上传失败: {e}", exc_info=True)
        return Response(
            {'error': '文件上传失败'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_documents(request):
    """
    获取用户上传的文档列表
    
    Query params:
        - conversation_id: 可选，筛选特定对话的文档
        - limit: 可选，限制返回数量（默认20）
    
    Response:
    {
        "documents": [
            {
                "id": 123,
                "title": "resume.pdf",
                "doc_type": "other",
                "file_size": 12345,
                "uploaded_at": "2025-11-30T12:34:56Z",
                "preview_url": "/media/uploads/..."
            }
        ],
        "total": 5
    }
    """
    try:
        conversation_id = request.query_params.get('conversation_id')
        limit = int(request.query_params.get('limit', 20))
        
        # 查询文档
        documents = AIDocument.objects.filter(uploaded_by=request.user)
        
        if conversation_id:
            documents = documents.filter(metadata__conversation_id=conversation_id)
        
        documents = documents.order_by('-created_at')[:limit]
        
        # 序列化
        result = []
        for doc in documents:
            file_path = doc.metadata.get('file_path', '')
            result.append({
                "id": doc.id,
                "title": doc.title,
                "doc_type": doc.doc_type,
                "file_size": doc.metadata.get('file_size', 0),
                "file_extension": doc.metadata.get('file_extension', ''),
                "uploaded_at": doc.created_at.isoformat(),
                "preview_url": default_storage.url(file_path) if file_path else None,
            })
        
        return Response({
            "documents": result,
            "total": AIDocument.objects.filter(uploaded_by=request.user).count(),
        })
        
    except Exception as e:
        logger.error(f"[文档列表] 获取失败: {e}", exc_info=True)
        return Response(
            {'error': '获取文档列表失败'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_document(request, document_id):
    """
    删除文档
    
    Response:
    {
        "message": "文档已删除"
    }
    """
    try:
        # 验证文档是否存在且属于当前用户
        try:
            document = AIDocument.objects.get(id=document_id, uploaded_by=request.user)
        except AIDocument.DoesNotExist:
            return Response(
                {'error': '文档不存在或无权访问'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 删除磁盘文件
        file_path = document.metadata.get('file_path')
        if file_path and default_storage.exists(file_path):
            try:
                default_storage.delete(file_path)
                logger.info(f"[文档删除] 磁盘文件已删除: {file_path}")
            except Exception as e:
                logger.warning(f"[文档删除] 磁盘文件删除失败: {e}")
        
        # 删除数据库记录
        document.delete()
        
        logger.info(f"[文档删除] 用户 {request.user.username} 删除文档: {document_id}")
        
        return Response({"message": "文档已删除"})
        
    except Exception as e:
        logger.error(f"[文档删除] 删除失败: {e}", exc_info=True)
        return Response(
            {'error': '删除文档失败'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_document(request, document_id):
    """
    分析文档内容（使用AI）
    
    Request body:
    {
        "task": "summarize",  # 任务类型: summarize, optimize, review, translate
        "instructions": "请总结这份简历的核心优势"  # 可选，自定义指令
    }
    
    Response:
    {
        "analysis": "...",
        "task": "summarize",
        "elapsed_ms": 1234
    }
    """
    try:
        # 验证文档是否存在且属于当前用户
        try:
            document = AIDocument.objects.get(id=document_id, uploaded_by=request.user)
        except AIDocument.DoesNotExist:
            return Response(
                {'error': '文档不存在或无权访问'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        task = request.data.get('task', 'summarize')
        custom_instructions = request.data.get('instructions', '')
        
        # 构建AI分析问题
        task_prompts = {
            'summarize': '请总结以下文档的核心内容和要点：',
            'optimize': '请分析以下文档并提出优化建议：',
            'review': '请审查以下文档，指出问题和改进方向：',
            'translate': '请将以下文档翻译为中文：',
        }
        
        task_prompt = task_prompts.get(task, task_prompts['summarize'])
        if custom_instructions:
            task_prompt = custom_instructions
        
        question = f"{task_prompt}\n\n【文档内容】\n{document.content[:5000]}"  # 限制长度
        
        # 调用AI
        try:
            ai_client = get_ai_client()
            system_prompt = get_system_prompt("prompts/generic.txt")
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ]
            
            import time
            start_time = time.time()
            answer = ai_client.chat_completion(messages=messages)
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            logger.info(
                f"[文档分析] 用户 {request.user.username} 分析文档 {document_id}, "
                f"任务: {task}, 耗时: {elapsed_ms}ms"
            )
            
            return Response({
                "analysis": answer,
                "task": task,
                "document_title": document.title,
                "elapsed_ms": elapsed_ms,
            })
            
        except Exception as e:
            logger.error(f"[文档分析] AI分析失败: {e}", exc_info=True)
            return Response(
                {'error': 'AI分析失败'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        logger.error(f"[文档分析] 请求处理失败: {e}", exc_info=True)
        return Response(
            {'error': '服务器内部错误'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
