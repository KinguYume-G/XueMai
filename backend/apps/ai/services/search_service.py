"""
实时搜索增强服务

支持通过搜索API获取最新信息，补充RAG知识库的不足
"""

import logging
import requests
from typing import List, Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class SearchService:
    """搜索服务 - 支持多种搜索引擎"""
    
    # 触发搜索的关键词
    SEARCH_TRIGGERS = [
        "最新", "现在", "当前", "今年", "今天", "实时",
        "最近", "latest", "current", "now", "today", "real-time"
    ]
    
    def __init__(self):
        # 配置搜索API（从环境变量读取）
        self.google_api_key = getattr(settings, 'GOOGLE_SEARCH_API_KEY', None)
        self.google_cx = getattr(settings, 'GOOGLE_SEARCH_CX', None)
        self.bing_api_key = getattr(settings, 'BING_SEARCH_API_KEY', None)
        
        # 确定使用哪个搜索引擎
        if self.google_api_key and self.google_cx:
            self.search_engine = 'google'
        elif self.bing_api_key:
            self.search_engine = 'bing'
        else:
            self.search_engine = 'duckduckgo'  # 免费但功能有限
            logger.warning("[搜索服务] 未配置搜索API，将使用DuckDuckGo（功能有限）")
    
    def should_search(self, query: str) -> bool:
        """
        判断是否需要触发搜索
        
        Args:
            query: 用户查询
        
        Returns:
            bool: 是否需要搜索
        """
        query_lower = query.lower()
        return any(trigger in query_lower for trigger in self.SEARCH_TRIGGERS)
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        执行搜索
        
        Args:
            query: 搜索查询
            max_results: 最大返回结果数
        
        Returns:
            List[Dict]: 搜索结果列表
        """
        try:
            if self.search_engine == 'google':
                return self._search_google(query, max_results)
            elif self.search_engine == 'bing':
                return self._search_bing(query, max_results)
            else:
                return self._search_duckduckgo(query, max_results)
        except Exception as e:
            logger.error(f"[搜索服务] 搜索失败: {e}", exc_info=True)
            return []
    
    def _search_google(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """使用Google Custom Search API搜索"""
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.google_api_key,
            "cx": self.google_cx,
            "q": query,
            "num": max_results,
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('items', []):
            results.append({
                "title": item.get('title', ''),
                "snippet": item.get('snippet', ''),
                "url": item.get('link', ''),
                "source": "google",
            })
        
        logger.info(f"[搜索服务] Google搜索成功，返回 {len(results)} 条结果")
        return results
    
    def _search_bing(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """使用Bing Search API搜索"""
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {
            "Ocp-Apim-Subscription-Key": self.bing_api_key,
        }
        params = {
            "q": query,
            "count": max_results,
            "mkt": "zh-CN",
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('webPages', {}).get('value', []):
            results.append({
                "title": item.get('name', ''),
                "snippet": item.get('snippet', ''),
                "url": item.get('url', ''),
                "source": "bing",
            })
        
        logger.info(f"[搜索服务] Bing搜索成功，返回 {len(results)} 条结果")
        return results
    
    def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """使用DuckDuckGo搜索（免费但功能有限）"""
        try:
            from duckduckgo_search import DDGS
            
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": r.get('title', ''),
                        "snippet": r.get('body', ''),
                        "url": r.get('href', ''),
                        "source": "duckduckgo",
                    })
            
            logger.info(f"[搜索服务] DuckDuckGo搜索成功，返回 {len(results)} 条结果")
            return results
            
        except ImportError:
            logger.error("[搜索服务] duckduckgo-search未安装")
            return []
        except Exception as e:
            logger.error(f"[搜索服务] DuckDuckGo搜索失败: {e}")
            return []
    
    def format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """
        格式化搜索结果为文本（用于注入到AI Prompt）
        
        Args:
            results: 搜索结果列表
        
        Returns:
            str: 格式化后的文本
        """
        if not results:
            return ""
        
        formatted_parts = ["【网络搜索结果】\n"]
        for i, result in enumerate(results, 1):
            formatted_parts.append(
                f"\n{i}. {result['title']}\n"
                f"来源：{result['url']}\n"
                f"摘要：{result['snippet']}\n"
            )
        
        return "\n".join(formatted_parts)


# 全局搜索服务单例
_search_service = None


def get_search_service() -> SearchService:
    """获取搜索服务单例"""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service



