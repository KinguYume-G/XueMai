"""
Groq客户端封装（超快速AI推理）
"""
from groq import Groq
from typing import List, Dict, Iterator
import time
import logging
import os

logger = logging.getLogger(__name__)

class GroqClient:
    """Groq客户端类"""
    
    def __init__(
        self,
        model: str = "llama-3.1-8b-instant",
        api_key: str = None
    ):
        """初始化Groq客户端"""
        self.model = model
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY未设置")
        
        self.client = Groq(api_key=self.api_key)
        logger.info(f"✅ Groq客户端初始化成功: {model}")
    
    def chat(self, messages: List[Dict[str, str]]) -> Dict[str, any]:
        """同步聊天"""
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
            )
            
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            return {
                "content": response.choices[0].message.content,
                "elapsed_ms": elapsed_ms
            }
        except Exception as e:
            logger.error(f"❌ Groq聊天失败: {e}")
            raise
    
    def stream_chat(self, messages: List[Dict[str, str]]) -> Iterator[str]:
        """流式聊天"""
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"❌ Groq流式聊天失败: {e}")
            raise