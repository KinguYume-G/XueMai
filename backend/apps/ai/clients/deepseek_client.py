"""
DeepSeek AI 客户端实现

使用 DeepSeek API 进行 AI 对话，支持流式和非流式输出。
"""

import logging
from typing import Dict, Iterator, List, Optional

import requests
from django.conf import settings

from .base import BaseAIClient

logger = logging.getLogger(__name__)


class DeepSeekClient(BaseAIClient):
    """
    DeepSeek 客户端实现

    调用 DeepSeek API，支持高质量的 AI 对话。
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "deepseek-chat",
        base_url: str = "https://api.deepseek.com",
        timeout: int = 60,
        **config,
    ):
        """
        初始化 DeepSeek 客户端

        Args:
            api_key: DeepSeek API 密钥（默认从 settings 读取）
            model: 模型名称
            base_url: API 基础 URL
            timeout: 请求超时时间（秒）
            **config: 其他配置参数
        """
        super().__init__(**config)
        self.api_key = api_key or getattr(settings, "DEEPSEEK_API_KEY", None)
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        if not self.api_key:
            raise ValueError("DeepSeek API 密钥未配置，请设置 DEEPSEEK_API_KEY")

        logger.info(f"初始化 DeepSeekClient: 模型 {self.model}")

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> str:
        """
        调用 DeepSeek Chat API（非流式）

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大 token 数
            **kwargs: 其他参数

        Returns:
            AI 回复内容

        Raises:
            requests.RequestException: 当 API 调用失败时
            ValueError: 当消息格式无效时
        """
        # 验证消息格式
        if not self.validate_messages(messages):
            raise ValueError("消息格式无效")

        # 构建请求头
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        # 构建请求数据
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

        # 添加额外参数
        if kwargs:
            payload.update(kwargs)

        try:
            logger.debug(f"调用 DeepSeek API: {self.base_url}/chat/completions")

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()

            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

            logger.info(f"DeepSeek 响应成功，内容长度: {len(content)}")
            return content

        except requests.HTTPError as e:
            self._handle_http_error(e)

        except requests.RequestException as e:
            logger.error(f"DeepSeek API 调用失败: {e}")
            raise Exception(f"DeepSeek API 调用失败: {str(e)}")

    def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> Iterator[str]:
        """
        调用 DeepSeek Chat API（流式输出）

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大 token 数
            **kwargs: 其他参数

        Yields:
            AI 回复的文本片段

        Raises:
            requests.RequestException: 当 API 调用失败时
            ValueError: 当消息格式无效时
        """
        # 验证消息格式
        if not self.validate_messages(messages):
            raise ValueError("消息格式无效")

        # 构建请求头
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        # 构建请求数据
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,  # 启用流式
        }

        # 添加额外参数
        if kwargs:
            payload.update(kwargs)

        try:
            logger.info(f"DeepSeek 流式调用开始: {self.model}")

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout,
                stream=True,  # 启用流式响应
            )
            response.raise_for_status()

            # 逐行读取 SSE 格式的响应
            for line in response.iter_lines():
                if line:
                    line = line.decode("utf-8")

                    # SSE 格式：data: {...}
                    if line.startswith("data: "):
                        data_str = line[6:]  # 去掉 "data: " 前缀

                        # 检查是否是结束信号
                        if data_str == "[DONE]":
                            logger.info("DeepSeek 流式调用完成")
                            break

                        try:
                            import json

                            data = json.loads(data_str)

                            # 提取内容片段
                            if "choices" in data and data["choices"]:
                                delta = data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content

                        except json.JSONDecodeError:
                            logger.warning(f"无法解析 JSON: {data_str}")
                            continue

        except requests.HTTPError as e:
            self._handle_http_error(e)

        except requests.RequestException as e:
            logger.error(f"DeepSeek 流式调用失败: {e}")
            raise Exception(f"DeepSeek 流式调用失败: {str(e)}")

    def get_model_name(self) -> str:
        """
        获取当前模型名称

        Returns:
            模型名称
        """
        return self.model

    def check_health(self) -> bool:
        """
        检查 DeepSeek API 健康状态

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

    def _handle_http_error(self, e: requests.HTTPError):
        """
        处理 HTTP 错误

        Args:
            e: HTTP 异常对象

        Raises:
            Exception: 带有友好错误消息的异常
        """
        status_code = e.response.status_code
        error_msg = e.response.text

        if status_code == 401:
            logger.error("DeepSeek API 密钥无效")
            raise Exception("DeepSeek API 密钥无效，请检查配置")
        elif status_code == 429:
            logger.error("DeepSeek API 请求频率超限")
            raise Exception("DeepSeek API 请求频率超限，请稍后重试")
        else:
            logger.error(f"DeepSeek API 错误 {status_code}: {error_msg}")
            raise Exception(f"DeepSeek API 调用失败: {error_msg}")
