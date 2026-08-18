"""
Base Crawler Class - Foundation for all web crawlers
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class BaseCrawler(ABC):
    """所有爬虫的基类"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化爬虫
        
        Args:
            config: 配置字典，包含rate_limit、timeout等
        """
        self.config = config or {}
        self.rate_limit = self.config.get('rate_limit', 2)  # 默认2秒延迟
        self.timeout = self.config.get('timeout', 10)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 初始化session
        self.session = self._init_session()
        
        self.logger.info(f"初始化 {self.__class__.__name__}")
        
    def _init_session(self) -> requests.Session:
        """初始化requests session"""
        session = requests.Session()
        
        # 设置User-Agent（明确标识为教育用途）
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Educational Research Bot) - UniPulse Asia Student Project',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        
        return session
    
    def check_robots_txt(self, url: str) -> bool:
        """
        检查robots.txt是否允许爬取
        
        Args:
            url: 要检查的URL
            
        Returns:
            True if allowed, False otherwise
        """
        try:
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            user_agent = self.session.headers.get('User-Agent', '*')
            allowed = rp.can_fetch(user_agent, url)
            
            if allowed:
                self.logger.info(f"✅ robots.txt允许爬取: {url}")
            else:
                self.logger.warning(f"❌ robots.txt禁止爬取: {url}")
                
            return allowed
            
        except Exception as e:
            self.logger.warning(f"无法检查robots.txt: {e}，假设允许")
            return True
    
    def fetch_page(self, url: str) -> Optional[str]:
        """
        获取网页内容
        
        Args:
            url: 目标URL
            
        Returns:
            HTML内容，失败返回None
        """
        try:
            self.logger.info(f"正在获取: {url}")
            
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            self.logger.info(f"✅ 成功获取 ({response.status_code}): {url}")
            
            # 延迟下次请求
            time.sleep(self.rate_limit)
            
            return response.text
            
        except requests.Timeout:
            self.logger.error(f"❌ 请求超时: {url}")
            return None
            
        except requests.HTTPError as e:
            self.logger.error(f"❌ HTTP错误 {e.response.status_code}: {url}")
            return None
            
        except requests.RequestException as e:
            self.logger.error(f"❌ 请求失败: {url} - {e}")
            return None
    
    def parse_html(self, html: str, parser: str = 'html.parser') -> Optional[BeautifulSoup]:
        """
        解析HTML
        
        Args:
            html: HTML字符串
            parser: BeautifulSoup解析器
            
        Returns:
            BeautifulSoup对象
        """
        try:
            soup = BeautifulSoup(html, parser)
            return soup
        except Exception as e:
            self.logger.error(f"❌ HTML解析失败: {e}")
            return None
    
    @abstractmethod
    def scrape(self) -> List[Dict]:
        """
        执行爬取（子类必须实现）
        
        Returns:
            爬取的数据列表
        """
        pass
    
    @abstractmethod
    def parse_page(self, soup: BeautifulSoup, url: str) -> Dict:
        """
        解析页面内容（子类必须实现）
        
        Args:
            soup: BeautifulSoup对象
            url: 页面URL
            
        Returns:
            结构化数据
        """
        pass

