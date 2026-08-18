"""
Ollama AI 客户端实现

使用本地 Ollama 服务进行 AI 对话，支持流式和非流式输出。
"""

import json
import logging
from typing import Dict, Iterator, List

import requests

from .base import BaseAIClient

logger = logging.getLogger(__name__)


class OllamaClient(BaseAIClient):
    """
    Ollama 客户端实现

    连接本地 Ollama 服务，支持多种开源模型。
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen3:8b",
        timeout: int = 60,
        think: bool = False,
        **config,
    ):
        """
        初始化 Ollama 客户端

        Args:
            base_url: Ollama 服务地址
            model: 模型名称（如 qwen3:8b, llama2, mistral）
            timeout: 请求超时时间（秒）
            **config: 其他配置参数
        """
        super().__init__(**config)
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        # Qwen 3 models can spend the entire output budget in the hidden
        # reasoning field and return an empty ``message.content``.  The API
        # endpoints expose the final answer only, so reasoning is disabled by
        # default.  It remains configurable for models/workflows that need it.
        self.think = think
        self.api_url = f"{self.base_url}/api/chat"

        logger.info(f"初始化 OllamaClient: {self.model} @ {self.base_url}")

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> str:
        """
        调用 Ollama Chat API（非流式）

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

        # 构建请求数据
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,  # 非流式
            "think": self.think,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        # 添加额外参数
        if kwargs:
            payload["options"].update(kwargs)

        try:
            logger.debug(f"调用 Ollama API: {self.api_url}")

            response = requests.post(self.api_url, json=payload, timeout=self.timeout)
            response.raise_for_status()

            result = response.json()
            content = result.get("message", {}).get("content", "")

            logger.info(f"Ollama 响应成功，内容长度: {len(content)}")
            return content

        except requests.Timeout:
            logger.error(f"Ollama 请求超时（{self.timeout}秒）")
            raise Exception(f"Ollama 请求超时，请检查服务是否正常运行")

        except requests.ConnectionError:
            logger.error(f"无法连接到 Ollama 服务: {self.base_url}")
            raise Exception(f"无法连接到 Ollama 服务，请确保服务已启动")

        except requests.RequestException as e:
            logger.error(f"Ollama API 调用失败: {e}")
            raise Exception(f"Ollama API 调用失败: {str(e)}")

    def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> Iterator[str]:
        """
        调用 Ollama Chat API（流式输出）

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

        # 构建请求数据
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,  # 启用流式
            "think": self.think,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        # 添加额外参数
        if kwargs:
            payload["options"].update(kwargs)

        try:
            logger.info(f"Ollama 流式调用开始: {self.model}")

            response = requests.post(
                self.api_url, json=payload, timeout=self.timeout, stream=True  # 关键：启用流式响应
            )
            response.raise_for_status()

            # 逐行读取响应
            for line in response.iter_lines():
                if line:
                    try:
                        # Ollama 返回的是 JSON 格式的行
                        data = json.loads(line)

                        # 提取内容片段
                        if "message" in data and "content" in data["message"]:
                            chunk = data["message"]["content"]
                            if chunk:
                                yield chunk

                        # 检查是否完成
                        if data.get("done", False):
                            logger.info("Ollama 流式调用完成")
                            break

                    except json.JSONDecodeError:
                        logger.warning(f"无法解析 JSON: {line}")
                        continue

        except requests.Timeout:
            logger.error(f"Ollama 流式请求超时（{self.timeout}秒）")
            raise Exception("Ollama 流式请求超时")

        except requests.ConnectionError:
            logger.error(f"无法连接到 Ollama 服务: {self.base_url}")
            raise Exception("无法连接到 Ollama 服务，请确保服务已启动")

        except requests.RequestException as e:
            logger.error(f"Ollama 流式调用失败: {e}")
            raise Exception(f"Ollama 流式调用失败: {str(e)}")

    def get_model_name(self) -> str:
        """
        获取当前模型名称

        Returns:
            模型名称
        """
        return self.model

    def list_models(self) -> List[str]:
        """
        列出所有可用模型

        Returns:
            模型名称列表
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()

            models = response.json().get("models", [])
            return [model["name"] for model in models]

        except Exception as e:
            logger.error(f"获取模型列表失败: {e}")
            return []

    def check_health(self) -> bool:
        """
        检查 Ollama 服务健康状态

        Returns:
            服务是否正常
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
