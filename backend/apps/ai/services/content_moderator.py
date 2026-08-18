"""
内容安全审核服务

功能：
1. 敏感词过滤
2. 个人隐私信息检测
3. 恶意输入防护
4. 有害内容拦截
"""

import re
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class ContentModerator:
    """内容审核器"""
    
    # 敏感词库（示例，实际应从配置文件加载）
    SENSITIVE_WORDS = [
        # 政治敏感词
        # ... (此处应添加具体的敏感词，但为了演示省略)
        
        # 色情暴力词汇
        # ... (此处应添加具体的词汇，但为了演示省略)
    ]
    
    # 个人隐私信息正则表达式
    PRIVACY_PATTERNS = {
        'phone': r'1[3-9]\d{9}',  # 手机号
        'id_card': r'\d{17}[\dXx]',  # 身份证号
        'email': r'[\w\.-]+@[\w\.-]+\.\w+',  # 邮箱（可能需要）
        'bank_card': r'\d{16,19}',  # 银行卡号
    }
    
    # SQL注入关键词
    SQL_INJECTION_KEYWORDS = [
        'drop table', 'delete from', 'insert into', 'update set',
        'union select', 'exec', 'execute', 'xp_', 'sp_',
        '--', ';--', '/*', '*/', 'chr(', 'char('
    ]
    
    # XSS攻击关键词
    XSS_KEYWORDS = [
        '<script', '</script>', '<iframe', 'javascript:', 'onerror=',
        'onclick=', 'onload=', 'eval(', 'alert(', 'document.cookie'
    ]
    
    def __init__(self):
        self.sensitive_words_set = set(word.lower() for word in self.SENSITIVE_WORDS)
    
    def moderate_input(self, text: str) -> Dict[str, Any]:
        """
        审核用户输入
        
        Args:
            text: 用户输入文本
        
        Returns:
            Dict: 审核结果
                {
                    "safe": bool,
                    "reasons": List[str],
                    "filtered_text": str  # 可选：过滤后的文本
                }
        """
        reasons = []
        
        # 1. 敏感词检测
        if self._contains_sensitive_words(text):
            reasons.append("包含敏感词汇")
        
        # 2. 隐私信息检测
        privacy_matches = self._detect_privacy_info(text)
        if privacy_matches:
            reasons.append(f"包含隐私信息：{', '.join(privacy_matches)}")
        
        # 3. SQL注入检测
        if self._detect_sql_injection(text):
            reasons.append("疑似SQL注入攻击")
        
        # 4. XSS攻击检测
        if self._detect_xss(text):
            reasons.append("疑似XSS攻击")
        
        # 5. 垃圾信息检测（简单规则）
        if self._is_spam(text):
            reasons.append("疑似垃圾信息")
        
        return {
            "safe": len(reasons) == 0,
            "reasons": reasons,
            "filtered_text": self._filter_text(text) if reasons else text,
        }
    
    def moderate_output(self, text: str) -> Dict[str, Any]:
        """
        审核AI输出
        
        Args:
            text: AI生成的文本
        
        Returns:
            Dict: 审核结果
        """
        reasons = []
        
        # 1. 敏感词检测
        if self._contains_sensitive_words(text):
            reasons.append("AI输出包含敏感词汇")
        
        # 2. 有害建议检测
        if self._contains_harmful_advice(text):
            reasons.append("AI输出包含有害建议")
        
        return {
            "safe": len(reasons) == 0,
            "reasons": reasons,
            "filtered_text": self._filter_text(text) if reasons else text,
        }
    
    def _contains_sensitive_words(self, text: str) -> bool:
        """检测敏感词"""
        text_lower = text.lower()
        for word in self.sensitive_words_set:
            if word in text_lower:
                logger.warning(f"[审核] 检测到敏感词: {word}")
                return True
        return False
    
    def _detect_privacy_info(self, text: str) -> List[str]:
        """检测隐私信息"""
        matches = []
        for name, pattern in self.PRIVACY_PATTERNS.items():
            if re.search(pattern, text):
                matches.append(name)
                logger.warning(f"[审核] 检测到隐私信息: {name}")
        return matches
    
    def _detect_sql_injection(self, text: str) -> bool:
        """检测SQL注入"""
        text_lower = text.lower()
        for keyword in self.SQL_INJECTION_KEYWORDS:
            if keyword in text_lower:
                logger.warning(f"[审核] 检测到SQL注入尝试: {keyword}")
                return True
        return False
    
    def _detect_xss(self, text: str) -> bool:
        """检测XSS攻击"""
        text_lower = text.lower()
        for keyword in self.XSS_KEYWORDS:
            if keyword in text_lower:
                logger.warning(f"[审核] 检测到XSS攻击尝试: {keyword}")
                return True
        return False
    
    def _is_spam(self, text: str) -> bool:
        """检测垃圾信息（简单规则）"""
        # 1. 过长的文本（可能是垃圾信息）
        if len(text) > 10000:
            return True
        
        # 2. 重复字符过多
        if re.search(r'(.)\1{20,}', text):
            return True
        
        # 3. 包含大量URL
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        if len(urls) > 5:
            return True
        
        return False
    
    def _contains_harmful_advice(self, text: str) -> bool:
        """检测有害建议"""
        harmful_keywords = [
            '作弊', '代考', '代写', '买卖答案', '盗版', '破解',
            '违法', '犯罪', '伪造', '欺诈', '诈骗',
        ]
        
        text_lower = text.lower()
        for keyword in harmful_keywords:
            if keyword in text_lower:
                logger.warning(f"[审核] AI输出包含有害建议: {keyword}")
                return True
        return False
    
    def _filter_text(self, text: str) -> str:
        """过滤文本（替换敏感词、隐私信息）"""
        filtered = text
        
        # 替换敏感词
        for word in self.sensitive_words_set:
            if word in filtered.lower():
                filtered = re.sub(re.escape(word), '*' * len(word), filtered, flags=re.IGNORECASE)
        
        # 脱敏隐私信息
        for name, pattern in self.PRIVACY_PATTERNS.items():
            def replace_with_mask(match):
                value = match.group()
                return value[:3] + '*' * (len(value) - 6) + value[-3:] if len(value) > 6 else '*' * len(value)
            
            filtered = re.sub(pattern, replace_with_mask, filtered)
        
        return filtered


# 全局内容审核器单例
_content_moderator = None


def get_content_moderator() -> ContentModerator:
    """获取内容审核器单例"""
    global _content_moderator
    if _content_moderator is None:
        _content_moderator = ContentModerator()
    return _content_moderator



