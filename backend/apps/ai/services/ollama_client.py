"""
Ollama客户端封装
提供与Ollama LLM的交互接口
"""

import logging
import time
from typing import Any, Dict, Iterator, List, Optional

from langchain_ollama import ChatOllama

logger = logging.getLogger(__name__)


class OllamaClient:
    """Thin wrapper around the ChatOllama interface."""

    def __init__(
        self,
        model: str = "llama3.1:8b",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
    ):
        """
        初始化Ollama客户端

        Args:
            model: Ollama模型名称
            base_url: Ollama服务地址
            temperature: 采样温度(0-1)
        """
        try:
            self.model = model
            self.base_url = base_url
            self.temperature = temperature

            self.llm = ChatOllama(
                model=model,
                base_url=base_url,
                temperature=temperature,
            )
            logger.info(f"✅ Ollama客户端初始化成功: {model} @ {base_url}")
        except Exception as e:
            logger.error(f"❌ Ollama客户端初始化失败: {e}")
            raise

    def chat(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        同步聊天

        Args:
            messages: 对话历史，格式: [{"role": "user", "content": "..."}]

        Returns:
            {"content": "回答内容", "elapsed_ms": 响应时间}
        """
        try:
            start_time = time.time()

            response = self.llm.invoke(messages)

            elapsed_ms = int((time.time() - start_time) * 1000)
            logger.info(f"Ollama聊天完成，耗时: {elapsed_ms}ms")

            return {
                "content": response.content,
                "elapsed_ms": elapsed_ms,
            }
        except Exception as e:
            logger.error(f"❌ Ollama聊天失败: {e}")
            raise

    def stream_chat(self, messages: List[Dict[str, str]]) -> Iterator[str]:
        """
        流式聊天

        Args:
            messages: 对话历史

        Yields:
            生成的文本片段
        """
        try:
            for chunk in self.llm.stream(messages):
                if hasattr(chunk, "content"):
                    yield chunk.content
        except Exception as e:
            logger.error(f"❌ Ollama流式聊天失败: {e}")
            raise
