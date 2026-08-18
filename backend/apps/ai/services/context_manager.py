"""
Context Manager Service - 管理对话上下文和Token计数

功能：
1. 获取指定对话的上下文消息（带Token限制）
2. 添加新消息并自动计算Token
3. 当超出Token限制时，智能压缩/截断旧消息
"""

import logging
import tiktoken
from typing import List, Dict, Any, Optional
from django.db import transaction

from apps.ai.models import AIConversation, AIMessage

logger = logging.getLogger(__name__)


class ContextManager:
    """对话上下文管理器"""
    
    def __init__(self, encoding_name: str = "cl100k_base"):
        """
        初始化 Context Manager
        
        Args:
            encoding_name: tiktoken 编码名称，默认使用 cl100k_base (适用于 GPT-3.5/4)
        """
        try:
            self.encoding = tiktoken.get_encoding(encoding_name)
            logger.info(f"[ContextManager] 使用 tiktoken 编码: {encoding_name}")
        except Exception as e:
            # tiktoken downloads its vocabulary on first use. Conversation
            # history must still work in offline/local development mode.
            self.encoding = None
            logger.warning(f"[ContextManager] tiktoken 不可用，使用本地估算: {e}")
    
    def count_tokens(self, text: str) -> int:
        """
        计算文本的Token数量
        
        Args:
            text: 要计算的文本
            
        Returns:
            Token数量
        """
        try:
            if not text:
                return 0

            if self.encoding is not None:
                return len(self.encoding.encode(text))

            # Chinese characters are commonly close to one token each, while
            # Latin text averages roughly four characters per token.
            cjk_chars = sum(1 for char in text if "\u3400" <= char <= "\u9fff")
            other_chars = len(text) - cjk_chars
            return max(1, cjk_chars + (other_chars + 3) // 4)
        except Exception as e:
            logger.error(f"[ContextManager] Token计数失败: {e}")
            # 降级方案：粗略估计 (1 token ≈ 4 字符)
            return max(1, (len(text) + 3) // 4) if text else 0
    
    def get_context_messages(
        self,
        conversation_id: int,
        max_tokens: int = 2000,
        include_system: bool = False
    ) -> List[Dict[str, str]]:
        """
        获取对话的上下文消息（按Token限制）
        
        策略：
        1. 始终保留最近的消息
        2. 当超出Token限制时，从旧消息开始截断
        3. 确保 user/assistant 消息成对出现
        
        Args:
            conversation_id: 对话ID
            max_tokens: 最大Token数量限制
            include_system: 是否包含system消息
            
        Returns:
            消息列表，格式为 [{"role": "user", "content": "..."}]
        """
        try:
            conversation = AIConversation.objects.get(id=conversation_id)
            
            # 获取所有消息（按时间正序）
            if include_system:
                messages = conversation.messages.all().order_by('created_at')
            else:
                messages = conversation.messages.filter(role__in=['user', 'assistant']).order_by('created_at')
            
            if not messages.exists():
                logger.info(f"[ContextManager] 对话 {conversation_id} 无历史消息")
                return []
            
            # 从最新消息开始倒序累积，直到超过Token限制
            result_messages = []
            total_tokens = 0
            
            # 反向遍历消息（从最新到最旧）
            for message in reversed(messages):
                msg_dict = {
                    "role": message.role,
                    "content": message.content
                }
                
                # 计算消息的Token数（如果已存储则使用，否则实时计算）
                if message.tokens > 0:
                    msg_tokens = message.tokens
                else:
                    msg_tokens = self.count_tokens(message.content)
                
                # 检查是否超出限制
                if total_tokens + msg_tokens > max_tokens:
                    # 已达到Token限制，停止添加更多消息
                    logger.info(
                        f"[ContextManager] 对话 {conversation_id} 已达到Token限制 "
                        f"({total_tokens}/{max_tokens})，截断旧消息"
                    )
                    break
                
                # 添加消息（注意：我们是反向遍历的）
                result_messages.insert(0, msg_dict)
                total_tokens += msg_tokens
            
            logger.info(
                f"[ContextManager] 对话 {conversation_id} 加载上下文: "
                f"{len(result_messages)} 条消息, {total_tokens} tokens"
            )
            
            return result_messages
            
        except AIConversation.DoesNotExist:
            logger.error(f"[ContextManager] 对话 {conversation_id} 不存在")
            return []
        except Exception as e:
            logger.error(f"[ContextManager] 获取上下文失败: {e}", exc_info=True)
            return []
    
    @transaction.atomic
    def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        model_used: str = "unknown"
    ) -> Optional[AIMessage]:
        """
        添加新消息到对话，并自动更新Token统计
        
        Args:
            conversation_id: 对话ID
            role: 消息角色 (user, assistant, system)
            content: 消息内容
            model_used: 使用的模型名称
            
        Returns:
            创建的消息对象，失败则返回 None
        """
        try:
            conversation = AIConversation.objects.get(id=conversation_id)
            
            # 计算Token数
            tokens = self.count_tokens(content)
            
            # 创建消息
            message = AIMessage.objects.create(
                conversation=conversation,
                role=role,
                content=content,
                tokens=tokens,
                model_used=model_used
            )
            
            # 更新对话的总Token数
            conversation.total_tokens += tokens
            conversation.save(update_fields=['total_tokens', 'updated_at'])
            
            logger.info(
                f"[ContextManager] 添加消息到对话 {conversation_id}: "
                f"role={role}, tokens={tokens}, 累计={conversation.total_tokens}"
            )
            
            return message
            
        except AIConversation.DoesNotExist:
            logger.error(f"[ContextManager] 对话 {conversation_id} 不存在")
            return None
        except Exception as e:
            logger.error(f"[ContextManager] 添加消息失败: {e}", exc_info=True)
            return None
    
    def get_conversation_summary(self, conversation_id: int, max_messages: int = 5) -> str:
        """
        生成对话摘要（用于上下文压缩）
        
        Args:
            conversation_id: 对话ID
            max_messages: 最多包含多少条最近的消息
            
        Returns:
            对话摘要文本
        """
        try:
            conversation = AIConversation.objects.get(id=conversation_id)
            recent_messages = conversation.messages.order_by('-created_at')[:max_messages]
            
            summary_parts = []
            for msg in reversed(recent_messages):
                prefix = "用户" if msg.role == "user" else "AI"
                # 截断过长的消息
                content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                summary_parts.append(f"{prefix}: {content}")
            
            return "\n".join(summary_parts)
            
        except AIConversation.DoesNotExist:
            logger.error(f"[ContextManager] 对话 {conversation_id} 不存在")
            return ""
        except Exception as e:
            logger.error(f"[ContextManager] 生成摘要失败: {e}", exc_info=True)
            return ""


# ========== 全局单例 ==========
_context_manager = None

def get_context_manager() -> ContextManager:
    """获取全局 ContextManager 单例"""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager






