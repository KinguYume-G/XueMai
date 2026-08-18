"""
Intent Recognition Service

智能识别用户查询意图，自动路由到最合适的AI功能。

识别策略（4层优先级链）:
1. 精确模式 - mode参数直接指定 → 0ms延迟
2. 关键词匹配 - 基于functions.yaml的keywords → ~10ms
3. 语义相似度 - embedding相似度匹配 → ~50ms
4. LLM分类 - 仅在前3层置信度<0.6时 → ~500ms
"""

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from django.conf import settings

logger = logging.getLogger(__name__)

# 缓存配置
_functions_config = None


@dataclass
class IntentResult:
    """意图识别结果"""

    function_id: str
    confidence: float
    method: str  # 'mode', 'keyword', 'semantic', 'llm'
    reasoning: str = ""


class IntentRecognizer:
    """
    意图识别器

    使用4层策略识别用户查询意图：
    1. mode参数直接指定（最高优先级）
    2. 关键词精确匹配
    3. 语义相似度（基于embedding）
    4. LLM分类（fallback）
    """

    def __init__(self):
        """初始化意图识别器"""
        self.config = self._load_config()
        self.embeddings = None  # 懒加载，避免启动时延迟

    def _load_config(self) -> Dict:
        """加载functions.yaml配置"""
        global _functions_config
        if _functions_config is None:
            config_path = Path(__file__).parent.parent / "config" / "functions.yaml"
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    _functions_config = yaml.safe_load(f)
                logger.info(f"加载配置成功：{len(_functions_config.get('functions', []))} 个功能")
            except Exception as e:
                logger.error(f"加载配置失败: {e}")
                _functions_config = {"functions": []}
        return _functions_config

    def recognize(
        self, query: str, mode: Optional[str] = None, user_context: Optional[Dict] = None
    ) -> IntentResult:
        """
        识别用户查询意图

        Args:
            query: 用户查询文本
            mode: 可选的指定模式（如果提供则直接返回）
            user_context: 用户上下文信息（暂未使用）

        Returns:
            IntentResult对象，包含识别的功能ID、置信度、方法和推理

        Example:
            >>> recognizer = IntentRecognizer()
            >>> result = recognizer.recognize("APU有什么计算机课程？")
            >>> print(result.function_id, result.confidence)
            'course_query', 0.95
        """
        if not query or not query.strip():
            return IntentResult("general", 0.5, "default", "查询为空，使用默认功能")

        query = query.strip()

        # Layer 1: 精确模式指定
        if mode:
            if self._is_valid_function(mode):
                return IntentResult(mode, 1.0, "mode", f"用户指定mode={mode}")
            else:
                logger.warning(f"无效的mode参数: {mode}，降级为自动识别")

        # Layer 2: 关键词匹配（最高优先级，快速且确定性强）
        keyword_result = self._keyword_match(query)
        if keyword_result and keyword_result.confidence >= 0.5:
            # 关键词匹配成功且置信度合理，直接返回
            return keyword_result
        
        # Layer 3: 语义相似度匹配（fallback，需要Ollama服务）
        semantic_result = self._semantic_match(query)
        if semantic_result and semantic_result.confidence >= 0.6:
            return semantic_result

        # Layer 4: 低置信度关键词（避免调用LLM）
        if keyword_result and keyword_result.confidence >= 0.3:
            return keyword_result

        # Layer 5: LLM分类（最后手段）
        llm_result = self._llm_classify(query)
        if llm_result and llm_result.confidence >= 0.6:
            return llm_result

        # 所有方法都失败，返回默认
        return IntentResult("general", 0.4, "default", "所有识别方法置信度不足，使用默认功能")

    def _is_valid_function(self, function_id: str) -> bool:
        """检查功能ID是否有效"""
        functions = self.config.get("functions", [])
        return any(f["id"] == function_id for f in functions)

    def _keyword_match(self, query: str) -> Optional[IntentResult]:
        """
        关键词匹配

        策略：
        - 查找query中是否包含任何关键词
        - 计算匹配的关键词数量
        - 置信度 = (匹配数 / 总关键词数) * 权重

        Returns:
            IntentResult或None
        """
        query_lower = query.lower()
        best_match = None
        best_score = 0

        for func in self.config.get("functions", []):
            keywords = func.get("keywords", [])
            if not keywords:
                continue

            # 计算匹配的关键词数
            matched_keywords = []
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in query_lower:
                    matched_keywords.append(keyword)

            if matched_keywords:
                # 置信度计算：匹配数越多，关键词越短（更精确），分数越高
                match_count = len(matched_keywords)
                avg_keyword_len = sum(len(k) for k in matched_keywords) / match_count

                # 基础分数
                score = match_count / len(keywords)

                # 关键词长度调整（长关键词更可靠）
                if avg_keyword_len >= 4:
                    score *= 1.2
                elif avg_keyword_len <= 2:
                    score *= 0.8

                # 多个关键词匹配，提升置信度
                if match_count >= 2:
                    score = min(score * 1.3, 1.0)

                if score > best_score:
                    best_score = score
                    best_match = func
                    matched_kw_str = ", ".join(matched_keywords)
                    reasoning = f"关键词匹配: {matched_kw_str}"

        if best_match:
            # 映射到0.5-0.95的置信度范围
            confidence = 0.5 + (best_score * 0.45)
            return IntentResult(
                best_match["id"], confidence, "keyword", reasoning if "reasoning" in locals() else ""
            )

        return None

    def _semantic_match(self, query: str) -> Optional[IntentResult]:
        """
        语义相似度匹配

        使用embedding计算query与每个功能的examples的相似度

        Returns:
            IntentResult或None
        """
        try:
            # 懒加载embeddings（避免启动延迟）
            if self.embeddings is None:
                from langchain_ollama import OllamaEmbeddings

                self.embeddings = OllamaEmbeddings(
                    model=settings.EMBEDDING_MODEL,
                    base_url=settings.OLLAMA_BASE_URL,
                )

            # 生成query的embedding
            query_embedding = self.embeddings.embed_query(query)

            best_match = None
            best_similarity = 0

            for func in self.config.get("functions", []):
                examples = func.get("examples", [])
                if not examples:
                    continue

                # 计算与所有examples的相似度
                for example in examples:
                    try:
                        example_embedding = self.embeddings.embed_query(example)

                        # 计算余弦相似度
                        similarity = self._cosine_similarity(query_embedding, example_embedding)

                        if similarity > best_similarity:
                            best_similarity = similarity
                            best_match = func
                            matched_example = example

                    except Exception as e:
                        logger.debug(f"计算embedding相似度失败: {e}")
                        continue

            if best_match and best_similarity > 0.5:
                # 相似度0.5-1.0 映射到 置信度0.6-0.9
                confidence = 0.6 + (best_similarity - 0.5) * 0.6
                reasoning = f"语义相似: '{matched_example}' (相似度={best_similarity:.2f})"
                return IntentResult(best_match["id"], confidence, "semantic", reasoning)

        except Exception as e:
            logger.warning(f"语义匹配失败: {e}，跳过此层")
            # 如果embedding服务不可用（例如Ollama未启动），静默失败

        return None

    def _llm_classify(self, query: str) -> Optional[IntentResult]:
        """
        LLM分类（fallback策略）

        使用轻量级模型进行意图分类

        Returns:
            IntentResult或None
        """
        try:
            from ..clients import get_ai_client

            # 构建分类prompt
            function_list = []
            for func in self.config.get("functions", []):
                function_list.append(f"- {func['id']}: {func['name']}")

            functions_str = "\n".join(function_list)

            system_prompt = f"""You are an intent classifier. Given a user query, identify which AI function is most appropriate.

Available functions:
{functions_str}

Respond with ONLY the function ID (e.g., "course_query"). If unsure, respond with "general"."""

            # 使用AI客户端（轻量级模型）
            ai_client = get_ai_client()
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query: {query}"},
            ]

            response = ai_client.chat_completion(messages, temperature=0.3, max_tokens=50)
            predicted_id = response.strip().lower()

            # 验证返回的ID
            if self._is_valid_function(predicted_id):
                return IntentResult(
                    predicted_id, 0.7, "llm", f"LLM分类: {predicted_id}"
                )
            else:
                logger.warning(f"LLM返回了无效的功能ID: {predicted_id}")
                return None

        except Exception as e:
            logger.error(f"LLM分类失败: {e}", exc_info=True)
            return None

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        计算两个向量的余弦相似度

        Args:
            vec1: 向量1
            vec2: 向量2

        Returns:
            相似度 (0-1)
        """
        # 简单的向量点积实现
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)


# 单例模式（可选，提升性能）
_recognizer_instance = None


def get_intent_recognizer() -> IntentRecognizer:
    """获取Intent Recognizer单例"""
    global _recognizer_instance
    if _recognizer_instance is None:
        _recognizer_instance = IntentRecognizer()
    return _recognizer_instance
