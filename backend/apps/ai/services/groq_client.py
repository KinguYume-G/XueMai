"""
Groq 客户端封装（超快速 AI 推理）

本模块提供 `GroqClient` 类，对 Groq 官方 Python SDK 进行简单封装，
支持同步与流式对话、日志记录、错误处理以及 token 数估算。
"""

from __future__ import annotations

import logging
import os
import re
import socket
import time
from typing import Dict, Generator, Iterable, List, Optional, Union

from groq import Groq

logger = logging.getLogger(__name__)


class GroqClient:
    """
    Groq 客户端类。

    功能特性：
    - 从环境变量自动读取 `GROQ_API_KEY` 与默认模型
    - 同步与流式对话（支持温度与最大 token 数配置）
    - 基于简单规则的 token 数估算（中/英文）
    - 完整的日志与错误处理（API 错误、网络错误、超时）
    """

    # 类属性 / 默认配置
    model_name: str
    default_temperature: float = 0.7
    default_max_tokens: int = 2000

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        """
        初始化 Groq 客户端。

        参数:
            model: 模型名称；若未提供，则从环境变量 `GROQ_DEFAULT_MODEL`
                   读取，若仍未设置，则回退到 `llama-3.1-8b-instant`。
            api_key: Groq API Key；若未提供，则从环境变量 `GROQ_API_KEY` 读取。

        异常:
            ValueError: 当 `GROQ_API_KEY` 未配置时抛出。
        """
        self.api_key: Optional[str] = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY 未设置，请在环境变量中配置。")

        self.model_name = model or os.getenv("GROQ_MODEL") or "llama-3.1-8b-instant"

        # 初始化 Groq 官方客户端
        self.client: Groq = Groq(api_key=self.api_key)
        logger.info("✅ Groq 客户端初始化成功: model=%s", self.model_name)

    def chat(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Union[str, Generator[str, None, None]]:
        """
        与 Groq 模型进行对话。

        参数:
            messages: 消息列表，格式与 Groq 官方 SDK 保持一致，
                      例如: [{"role": "user", "content": "你好"}]
            stream: 是否启用流式输出。
            temperature: 采样温度（0-2）；若为 None，则使用
                        `default_temperature`。
            max_tokens: 最大输出 token 数；若为 None，则使用
                        `default_max_tokens`。

        返回:
            - 当 `stream=False` 时，返回完整响应字符串。
            - 当 `stream=True` 时，返回一个 `Generator[str, None, None]`
              按顺序产出文本片段。

        异常:
            RuntimeError: 当发生 API 错误、网络错误或超时时抛出。
        """
        temperature = float(temperature) if temperature is not None else self.default_temperature
        max_tokens = int(max_tokens) if max_tokens is not None else self.default_max_tokens

        # 记录请求日志（对消息内容做长度截断，避免日志过长）
        safe_messages_repr = str(messages)
        if len(safe_messages_repr) > 1000:
            safe_messages_repr = safe_messages_repr[:1000] + "...(truncated)"

        logger.info(
            "Groq chat 请求: model=%s, stream=%s, temperature=%s, max_tokens=%s, messages=%s",
            self.model_name,
            stream,
            temperature,
            max_tokens,
            safe_messages_repr,
        )

        if stream:
            # 返回一个生成器，由调用方消费
            return self._stream_handler(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            elapsed_ms = int((time.time() - start_time) * 1000)

            content: str = (response.choices[0].message.content if response.choices else "") or ""

            logger.info(
                "Groq chat 响应成功: elapsed=%sms, content_preview=%s",
                elapsed_ms,
                content[:200] + ("...(truncated)" if len(content) > 200 else ""),
            )
            return content

        except TimeoutError as exc:
            logger.error("❌ Groq chat 超时: %s", exc, exc_info=True)
            raise RuntimeError("Groq chat 请求超时") from exc
        except (socket.error, OSError) as exc:
            logger.error("❌ Groq chat 网络错误: %s", exc, exc_info=True)
            raise RuntimeError("Groq chat 请求网络错误") from exc
        except Exception as exc:
            logger.exception("❌ Groq chat API 调用失败")
            raise RuntimeError(f"Groq chat API 调用失败: {exc}") from exc

    def _stream_handler(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> Generator[str, None, None]:
        """
        处理 Groq 流式响应的私有方法。

        参数:
            messages: 消息列表。
            temperature: 采样温度。
            max_tokens: 最大输出 token 数。

        返回:
            一个生成器，逐个产出文本 chunk（自动跳过空 chunk）。

        异常:
            RuntimeError: 当发生 API 错误、网络错误或超时时抛出。
        """
        start_time = time.time()
        try:
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            total_chars = 0
            for chunk in stream:
                if not chunk or not getattr(chunk, "choices", None):
                    continue

                delta = chunk.choices[0].delta
                # 兼容性处理：某些 SDK 版本中 delta 可能为 None
                if not delta:
                    continue

                piece: Optional[str] = getattr(delta, "content", None)
                if not piece:
                    continue

                total_chars += len(piece)
                yield piece

            elapsed_ms = int((time.time() - start_time) * 1000)
            logger.info(
                "Groq stream 结束: elapsed=%sms, total_chars=%s",
                elapsed_ms,
                total_chars,
            )

        except TimeoutError as exc:
            logger.error("❌ Groq stream 超时: %s", exc, exc_info=True)
            raise RuntimeError("Groq stream 请求超时") from exc
        except (socket.error, OSError) as exc:
            logger.error("❌ Groq stream 网络错误: %s", exc, exc_info=True)
            raise RuntimeError("Groq stream 请求网络错误") from exc
        except Exception as exc:
            logger.exception("❌ Groq stream API 调用失败")
            raise RuntimeError(f"Groq stream API 调用失败: {exc}") from exc

    def count_tokens(self, text: str) -> int:
        """
        估算文本对应的大致 token 数。

        简化规则（经验值，仅用于粗略估算，不等价于真实 tokenizer）：
        - 中文: 按 1.5 字 / token 估算；
        - 英文（及其它非中日韩字符）: 按 4 字符 / token 估算。

        参数:
            text: 待估算的文本内容。

        返回:
            估算得到的 token 数（四舍五入为整数）。
        """
        if not text:
            return 0

        # 区分中文与非中文字符
        chinese_chars = re.findall(r"[\u4e00-\u9fff]", text)
        num_chinese = len(chinese_chars)

        # 去掉中文后，剩余的字符按英文等 4 字符 / token 估算
        non_chinese_text = re.sub(r"[\u4e00-\u9fff]", "", text)
        num_non_chinese = len(non_chinese_text)

        chinese_tokens = num_chinese / 1.5  # 中文 1.5 字 / token
        english_tokens = num_non_chinese / 4.0  # 英文等 4 字符 / token

        estimated = chinese_tokens + english_tokens
        return int(estimated + 0.5)  # 四舍五入
