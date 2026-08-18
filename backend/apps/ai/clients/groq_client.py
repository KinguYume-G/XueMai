"""
Groq AI 客户端实现

使用 Groq 云端 API 进行高速 AI 对话，支持流式和非流式输出。
"""

import logging
from typing import Dict, Iterator, List, Optional

from django.conf import settings
from groq import Groq

from .base import BaseAIClient

logger = logging.getLogger(__name__)


class GroqClient(BaseAIClient):
    """
    Groq 客户端实现

    调用 Groq API，支持高质量的 AI 对话。
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "qwen/qwen3.6-27b",
        timeout: int = 30,
        **config,
    ):
        """
        初始化 Groq 客户端

        Args:
            api_key: Groq API 密钥（默认从 settings 读取）
            model: 模型名称
            timeout: 请求超时时间（秒）
            **config: 其他配置参数
        """
        super().__init__(**config)
        self.api_key = api_key or getattr(settings, "GROQ_API_KEY", None)
        self.model = model
        self.timeout = timeout

        if not self.api_key:
            raise ValueError("Groq API 密钥未配置，请设置 GROQ_API_KEY")

        # 初始化 Groq 客户端
        self.client = Groq(api_key=self.api_key)

        logger.info(f"初始化 GroqClient: 模型 {self.model}")

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> str:
        """
        调用 Groq Chat API（非流式）

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大 token 数
            **kwargs: 其他参数

        Returns:
            AI 回复内容

        Raises:
            Exception: 当 API 调用失败时
            ValueError: 当消息格式无效时
        """
        # 验证消息格式
        if not self.validate_messages(messages):
            raise ValueError("消息格式无效")

        try:
            logger.debug(f"调用 Groq API: 模型 {self.model}")

            # 调用 Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,  # 非流式
                **kwargs,
            )

            content = response.choices[0].message.content

            logger.info(f"Groq 响应成功，内容长度: {len(content)}")
            return content

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Groq API 调用失败: {error_msg}")
            self._handle_error(e)

    def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> Iterator[str]:
        """
        调用 Groq Chat API（流式输出）

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大 token 数
            **kwargs: 其他参数

        Yields:
            AI 回复的文本片段

        Raises:
            Exception: 当 API 调用失败时
            ValueError: 当消息格式无效时
        """
        # 验证消息格式
        if not self.validate_messages(messages):
            raise ValueError("消息格式无效")

        try:
            logger.info(f"Groq 流式调用开始: {self.model}")

            # 调用 Groq API（流式）
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,  # 启用流式
                **kwargs,
            )

            # 逐块返回内容
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

            logger.info("Groq 流式调用完成")

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Groq 流式调用失败: {error_msg}")
            self._handle_error(e)

    def get_model_name(self) -> str:
        """
        获取当前模型名称

        Returns:
            模型名称
        """
        return self.model

    def check_health(self) -> bool:
        """
        检查 Groq API 健康状态

        Returns:
            API 是否可用
        """
        try:
            # 发送一个简单的测试请求
            test_messages = [{"role": "user", "content": "Hi"}]
            self.chat_completion(test_messages, max_tokens=10)
            return True
        except:
            return False

    def _handle_error(self, e: Exception):
        """
        统一错误处理

        Args:
            e: 异常对象

        Raises:
            Exception: 带有友好错误消息的异常
        """
        error_msg = str(e).lower()

        if "api_key" in error_msg or "unauthorized" in error_msg:
            raise Exception("Groq API 密钥无效，请检查配置")
        elif "rate_limit" in error_msg:
            raise Exception("Groq API 请求频率超限，请稍后重试")
        elif "timeout" in error_msg:
            raise Exception("Groq API 请求超时")
        else:
            raise Exception(f"Groq API 调用失败: {str(e)}")
