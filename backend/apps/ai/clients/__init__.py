"""
AI 客户端工厂

提供统一的客户端创建和管理接口。
"""

import logging
from typing import Optional

from django.conf import settings

from .base import BaseAIClient
from .deepseek_client import DeepSeekClient
from .groq_client import GroqClient
from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)

# 导出所有客户端类
__all__ = [
    "BaseAIClient",
    "OllamaClient",
    "GroqClient",
    "DeepSeekClient",
    "get_ai_client",
    "AIClientType",
]


class AIClientType:
    """AI 客户端类型常量"""

    OLLAMA = "ollama"
    GROQ = "groq"
    DEEPSEEK = "deepseek"


def get_ai_client(client_type: Optional[str] = None, **kwargs) -> BaseAIClient:
    """
    AI 客户端工厂函数

    根据配置或参数创建对应的 AI 客户端实例。

    Args:
        client_type: 客户端类型 ('ollama', 'groq' 或 'deepseek')
                    如果为 None，则从 settings.AI_CLIENT_TYPE 读取
        **kwargs: 传递给客户端的额外参数

    Returns:
        AI 客户端实例

    Raises:
        ValueError: 当客户端类型无效时

    Examples:
        >>> # 使用默认配置（Groq）
        >>> client = get_ai_client()

        >>> # 指定使用 Ollama
        >>> client = get_ai_client('ollama', model='qwen3:8b')

        >>> # 指定使用 Groq
        >>> client = get_ai_client('groq')
    """
    # 从配置或参数获取客户端类型
    if client_type is None:
        client_type = getattr(settings, "AI_CLIENT_TYPE", AIClientType.GROQ)

    client_type = client_type.lower()

    logger.info(f"创建 AI 客户端: {client_type}")

    # 根据类型创建客户端
    if client_type == AIClientType.OLLAMA:
        # Ollama 配置
        config = {
            "base_url": getattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434"),
            "model": getattr(settings, "OLLAMA_MODEL", "qwen3:8b"),
            "timeout": getattr(settings, "OLLAMA_TIMEOUT", 60),
            "think": getattr(settings, "OLLAMA_THINK", False),
        }
        config.update(kwargs)
        return OllamaClient(**config)

    elif client_type == AIClientType.GROQ:
        # Groq 配置
        config = {
            "api_key": getattr(settings, "GROQ_API_KEY", None),
            "model": getattr(settings, "GROQ_MODEL", "qwen/qwen3.6-27b"),
            "timeout": getattr(settings, "GROQ_TIMEOUT", 30),
        }
        config.update(kwargs)
        return GroqClient(**config)

    elif client_type == AIClientType.DEEPSEEK:
        # DeepSeek 配置
        config = {
            "api_key": getattr(settings, "DEEPSEEK_API_KEY", None),
            "model": getattr(settings, "DEEPSEEK_MODEL", "deepseek-chat"),
            "base_url": getattr(settings, "DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            "timeout": getattr(settings, "DEEPSEEK_TIMEOUT", 60),
        }
        config.update(kwargs)
        return DeepSeekClient(**config)

    else:
        raise ValueError(
            f"不支持的 AI 客户端类型: {client_type}。"
            f"支持的类型: {AIClientType.OLLAMA}, {AIClientType.GROQ}, {AIClientType.DEEPSEEK}"
        )


def get_default_client() -> BaseAIClient:
    """
    获取默认的 AI 客户端

    使用 settings.AI_CLIENT_TYPE 配置的客户端。

    Returns:
        默认 AI 客户端实例
    """
    return get_ai_client()
