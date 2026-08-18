"""
AI应用 URL配置

提供以下API端点：
- /api/ai/health/ - 健康检查
- /api/ai/chat/stream/ - 流式聊天（SSE）
- /api/ai/chat/sync/ - 同步聊天

Phase 2: 多轮对话管理端点
- /api/ai/conversations/ - 创建对话、获取对话列表
- /api/ai/conversations/<id>/ - 获取对话详情、删除对话
- /api/ai/conversations/<id>/chat/ - 在对话中发送消息

Phase 4: API 增强端点
- /api/ai/functions/ - 获取所有 AI 功能列表
- /api/ai/prompts/ - 获取所有 Prompt 列表（调试）
- /api/ai/intent/test/ - 测试意图识别（调试）
"""

from django.urls import path

from . import views
from . import views_workflow  # 工作流相关视图
from . import views_upload  # 文件上传相关视图
from . import views_orchestrator  # Orchestrator相关视图

app_name = "ai"

urlpatterns = [
    # 健康检查端点
    path("health/", views.ai_health, name="health"),
    
    # 流式聊天端点（推荐使用）
    path("chat/stream/", views.ai_chat_stream, name="chat-stream"),
    
    # 同步聊天端点（简单场景）
    path("chat/sync/", views.ai_chat_sync, name="chat-sync"),
    
    # ========== Phase 2: 多轮对话管理 ==========
    # 对话列表（GET）和创建对话（POST）
    path("conversations/", views.ai_conversation_list, name="conversation-list"),
    
    # 对话详情（GET）和删除（DELETE）
    path("conversations/<int:conversation_id>/", views.ai_conversation_detail, name="conversation-detail"),
    
    # 在对话中发送消息（POST）
    path("conversations/<int:conversation_id>/chat/", views.ai_conversation_chat, name="conversation-chat"),
    
    # 获取对话的所有消息（GET）- 轻量级端点，用于前端历史加载
    path("conversations/<int:conversation_id>/messages/", views.get_conversation_messages, name="conversation-messages"),
    
    # ========== Phase 4: API 增强 ==========
    # 获取所有 AI 功能列表
    path("functions/", views.ai_functions_list, name="functions-list"),
    
    # 测试意图识别
    path("intent/test/", views.ai_intent_test, name="intent-test"),
    
    # 获取 Prompt 列表
    path("prompts/", views.ai_prompts_list, name="prompts-list"),
    
    # ========== Phase 6: 工作流编排系统 ==========
    # 执行工作流（流式）
    path("workflow/execute/", views_workflow.workflow_execute_stream, name="workflow-execute"),
    
    # 获取工作流模板列表
    path("workflow/templates/", views_workflow.workflow_templates_list, name="workflow-templates"),
    
    # 获取工作流状态
    path("workflow/status/<str:workflow_id>/", views_workflow.workflow_status, name="workflow-status"),
    
    # ========== Phase 7: Orchestrator AI编排器 ==========
    # 执行Orchestrator工作流（流式）
    path("orchestrator/execute/", views_orchestrator.orchestrator_execute_stream, name="orchestrator-execute"),
    
    # 获取可用工作流列表
    path("orchestrator/workflows/", views_orchestrator.orchestrator_workflows_list, name="orchestrator-workflows"),
    
    # ========== Phase 6: 多模态支持（文件上传）==========
    # 上传文件
    path("upload/", views_upload.upload_file, name="upload-file"),
    
    # 获取文档列表
    path("documents/", views_upload.list_documents, name="list-documents"),
    
    # 删除文档
    path("documents/<int:document_id>/", views_upload.delete_document, name="delete-document"),
    
    # 分析文档
    path("documents/<int:document_id>/analyze/", views_upload.analyze_document, name="analyze-document"),
]
