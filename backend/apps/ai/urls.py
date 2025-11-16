"""
AI应用URL配置
"""

from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    # 流式聊天（主要使用）
    path('chat/stream/', views.ai_chat_stream, name='chat_stream'),
    
    # 同步聊天（备用）
    path('chat/sync/', views.ai_chat_sync, name='chat_sync'),
    
    # 健康检查
    path('health/', views.ai_health, name='health'),
]