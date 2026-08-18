"""
Ollama AI 客户端实现

使用本地 Ollama 服务进行 AI 对话，支持流式和非流式输出。
"""

import base64
import json
import logging
import re
from typing import Dict, Iterator, List, Optional

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
        vision_model: str = "llama3.2-vision:11b",
        **config,
    ):
        """
        初始化 Ollama 客户端

        Args:
            base_url: Ollama 服务地址
            model: 模型名称（如 qwen3:8b, llama2, mistral）
            timeout: 请求超时时间（秒）
            vision_model: 用于图片/视频帧分析的多模态模型名称
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
        self.vision_model = vision_model
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

    _REPEAT_LOOP_RE = re.compile(r"(.{4,200}?)\1{2,}", re.DOTALL)

    @classmethod
    def _trim_repetition_loop(cls, text: str, max_repeats: int = 2) -> str:
        """
        修剪模型输出中的复读循环

        小参数量的量化视觉模型（尤其在用非主要训练语言如中文生成较长
        文本时）有时会在正确描述完内容后陷入复读循环，且退化模式并不
        统一：可能是词/短语级别的紧密复读（如"...的下方有一个小黑点的
        下方有一个小黑点..."，中间没有任何标点分隔），也可能是整句或
        整段级别的重复（甚至间隔穿插）。这里做两道防线：

        1) 用回溯引用正则检测任意 4~200 字符的片段连续重复 3 次及以上，
           命中即在该片段首次出现处截断——这能捕获不依赖标点分隔的
           紧密复读。
        2) 再按句子粒度（中/英文句末标点或换行切分）去重，处理间隔
           穿插、跨越较大片段的重复句子。
        """
        match = cls._REPEAT_LOOP_RE.search(text)
        if match:
            text = text[: match.start() + len(match.group(1))]

        sentences = re.split(r"(?<=[。！？!?\n])", text)
        seen_counts: Dict[str, int] = {}
        kept = []
        for sentence in sentences:
            key = sentence.strip()
            if not key:
                kept.append(sentence)
                continue
            seen_counts[key] = seen_counts.get(key, 0) + 1
            if seen_counts[key] > max_repeats:
                break
            kept.append(sentence)
        return "".join(kept).strip()

    def analyze_image(
        self,
        image_bytes: bytes,
        prompt: Optional[str] = None,
        temperature: float = 0.4,
        max_tokens: int = 500,
    ) -> str:
        """
        使用本地多模态视觉模型（如 llama3.2-vision）分析图片内容

        Args:
            image_bytes: 图片原始字节数据
            prompt: 分析指令，默认使用通用图片描述提示词
            temperature: 温度参数
            max_tokens: 最大生成 token 数

        Returns:
            AI 对图片内容的文字描述

        Raises:
            Exception: 当 API 调用失败或视觉模型不可用时
        """
        if prompt is None:
            prompt = (
                "请用中文详细描述这张图片的内容：图片类型（照片/截图/图表/文档等）、"
                "主要对象或场景、任何可见的文字（请完整准确地转录），"
                "以及其他有助于理解图片的细节。"
            )

        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        payload = {
            "model": self.vision_model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_b64],
                }
            ],
            "stream": False,
            "think": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                # 量化视觉模型在生成中文长文本时容易陷入复读循环，
                # 提高重复惩罚以降低其发生概率（配合下方的复读修剪兜底）。
                "repeat_penalty": 1.4,
                "repeat_last_n": 256,
            },
        }

        # 视觉模型推理通常比纯文本模型慢，且首次调用需要把模型（约10GB+）
        # 加载进显存/内存，给予更宽松的超时时间
        timeout = max(self.timeout, 180)

        try:
            logger.info(f"调用 Ollama 视觉模型: {self.vision_model} @ {self.base_url}")

            response = requests.post(self.api_url, json=payload, timeout=timeout)
            response.raise_for_status()

            result = response.json()
            content = result.get("message", {}).get("content", "")
            content = self._trim_repetition_loop(content)

            logger.info(f"视觉模型响应成功，描述长度: {len(content)}")
            return content

        except requests.Timeout:
            logger.error(f"视觉模型请求超时（{timeout}秒）")
            raise Exception("视觉模型请求超时，请稍后重试")

        except requests.ConnectionError:
            logger.error(f"无法连接到 Ollama 服务: {self.base_url}")
            raise Exception("无法连接到 Ollama 服务，请确保服务已启动，且已拉取视觉模型")

        except requests.RequestException as e:
            logger.error(f"视觉模型调用失败: {e}")
            raise Exception(f"视觉模型调用失败: {str(e)}")

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
