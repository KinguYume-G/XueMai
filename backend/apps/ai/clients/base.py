"""
AI 客户端基类

定义统一的 AI 客户端接口，所有具体实现必须继承此基类。
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Iterator, List, Optional

logger = logging.getLogger(__name__)


class BaseAIClient(ABC):
    """
    AI 客户端抽象基类

    定义统一的 AI 调用接口，支持：
    - 简单对话（chat_completion）
    - 流式输出（chat_completion_stream）

    所有 AI 客户端（Ollama、Groq、DeepSeek 等）都必须实现此接口。
    """

    def __init__(self, **config):
        """
        初始化 AI 客户端

        Args:
            **config: 客户端配置参数
        """
        self.config = config

    @abstractmethod
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> str:
        """
        对话补全（非流式）

        Args:
            messages: 消息列表，格式：[{"role": "user", "content": "..."}]
                     role 可以是: "system", "user", "assistant"
            temperature: 温度参数，控制随机性 (0.0-1.0)
            max_tokens: 最大生成 token 数
            **kwargs: 其他客户端特定参数

        Returns:
            完整的 AI 回复内容（字符串）

        Raises:
            Exception: 当 API 调用失败时
        """
        pass

    @abstractmethod
    def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> Iterator[str]:
        """
        对话补全（流式输出）

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大 token 数
            **kwargs: 其他参数

        Yields:
            AI 回复的文本片段

        Raises:
            Exception: 当 API 调用失败时

        Example:
            >>> client = get_ai_client()
            >>> for chunk in client.chat_completion_stream(messages):
            ...     print(chunk, end='', flush=True)
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        获取当前使用的模型名称

        Returns:
            模型名称字符串
        """
        pass

    def validate_messages(self, messages: List[Dict[str, str]]) -> bool:
        """
        验证消息格式是否正确

        Args:
            messages: 消息列表

        Returns:
            是否有效
        """
        if not isinstance(messages, list) or len(messages) == 0:
            logger.error("消息列表不能为空")
            return False

        valid_roles = {"system", "user", "assistant"}

        for msg in messages:
            if not isinstance(msg, dict):
                logger.error(f"消息必须是字典类型: {msg}")
                return False

            if "role" not in msg or "content" not in msg:
                logger.error(f"消息缺少 role 或 content: {msg}")
                return False

            if msg["role"] not in valid_roles:
                logger.error(f"无效的 role: {msg['role']}")
                return False

        return True
