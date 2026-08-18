"""
创业新闻爬虫 - 基于RSS订阅
爬取TechCrunch、e27、Tech in Asia等科技媒体的创业新闻
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List

import feedparser
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent))
from base_crawler import BaseCrawler


class NewsCrawler(BaseCrawler):
    """创业新闻爬虫（RSS）"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def scrape_rss(self, rss_url: str, max_items: int = 10) -> List[Dict]:
        """
        爬取RSS Feed
        
        Args:
            rss_url: RSS订阅地址
            max_items: 最大文章数量
            
        Returns:
            文章列表
        """
        self.logger.info(f"开始爬取RSS: {rss_url}")
        
        try:
            # 解析RSS
            feed = feedparser.parse(rss_url)
            
            if feed.bozo:
                self.logger.error(f"❌ RSS解析失败: {feed.bozo_exception}")
                return []
            
            self.logger.info(f"✅ RSS解析成功，共 {len(feed.entries)} 条")
            
            articles = []
            
            for i, entry in enumerate(feed.entries[:max_items]):
                try:
                    # 提取基本信息
                    article = {
                        'title': entry.get('title', 'Untitled'),
                        'summary': entry.get('summary', entry.get('description', '')),
                        'link': entry.get('link', ''),
                        'published': entry.get('published', entry.get('updated', '')),
                        'author': entry.get('author', 'Unknown'),
                        'source': feed.feed.get('title', 'Unknown')
                    }
                    
                    # 尝试获取完整内容
                    if 'content' in entry:
                        # 有些RSS包含完整内容
                        content = entry.content[0].value
                        article['content'] = self._clean_html(content)
                    else:
                        # 如果没有完整内容，尝试访问原文
                        article['content'] = article['summary']
                        self.logger.debug(f"  使用摘要作为内容（RSS未提供完整内容）")
                    
                    # 清理HTML标签
                    article['summary'] = self._clean_html(article['summary'])
                    article['content'] = self._clean_html(article['content'])
                    
                    # 添加元数据
                    article['category'] = 'startup'
                    article['subcategory'] = 'news'
                    article['scraped_at'] = datetime.now().isoformat()
                    article['content_length'] = len(article['content'])
                    
                    articles.append(article)
                    
                    self.logger.info(f"  ✅ [{i+1}/{max_items}] {article['title'][:50]}...")
                    
                except Exception as e:
                    self.logger.error(f"  ❌ 解析条目失败: {e}")
            
            return articles
            
        except Exception as e:
            self.logger.error(f"❌ RSS爬取失败: {e}")
            return []
    
    def _clean_html(self, html_text: str) -> str:
        """清理HTML标签"""
        if not html_text:
            return ""
        
        soup = BeautifulSoup(html_text, 'html.parser')
        
        # 移除脚本和样式
        for script in soup(['script', 'style']):
            script.decompose()
        
        # 获取文本
        text = soup.get_text()
        
        # 清理空白
        lines = [line.strip() for line in text.split('\n')]
        lines = [line for line in lines if line]
        
        return '\n'.join(lines)
    
    def scrape(self, rss_urls: List[str] = None, max_items: int = 10) -> List[Dict]:
        """
        爬取多个RSS源
        
        Args:
            rss_urls: RSS地址列表
            max_items: 每个源的最大文章数
            
        Returns:
            所有文章列表
        """
        if rss_urls is None:
            # 默认：TechCrunch RSS
            rss_urls = ['https://techcrunch.com/feed/']
        
        all_articles = []
        
        for rss_url in rss_urls:
            articles = self.scrape_rss(rss_url, max_items)
            all_articles.extend(articles)
            
            # RSS订阅是合法的，但仍然延迟
            import time
            time.sleep(self.rate_limit)
        
        self.logger.info(f"爬取完成，共获取 {len(all_articles)} 篇文章")
        return all_articles
    
    def parse_page(self, soup: BeautifulSoup, url: str) -> Dict:
        """基类要求实现（RSS不需要）"""
        return {}
    
    def save_to_json(self, data: List[Dict], output_path: str):
        """保存数据到JSON"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 添加元数据
            output_data = {
                "metadata": {
                    "total_articles": len(data),
                    "created_at": datetime.now().isoformat(),
                    "source": "Startup News RSS Feeds",
                    "data_type": "news_articles",
                    "version": "1.0"
                },
                "articles": data
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"✅ 数据已保存到: {output_path}")
            self.logger.info(f"文件大小: {output_file.stat().st_size / 1024:.2f} KB")
            
        except Exception as e:
            self.logger.error(f"❌ 保存失败: {e}")


def main():
    """主函数：测试RSS爬虫"""
    print("=" * 80)
    print("📰 创业新闻爬虫 - RSS测试运行")
    print("=" * 80)
    
    # 配置
    config = {
        'rate_limit': 2,  # 2秒延迟
        'timeout': 10
    }
    
    # 创建爬虫
    crawler = NewsCrawler(config)
    
    # TechCrunch RSS
    print("\n正在爬取TechCrunch RSS...")
    print("RSS地址: https://techcrunch.com/feed/")
    
    articles = crawler.scrape(
        rss_urls=['https://techcrunch.com/feed/'],
        max_items=10
    )
    
    # 统计
    print(f"\n✅ 成功爬取 {len(articles)} 篇文章")
    
    if articles:
        total_length = sum(a['content_length'] for a in articles)
        avg_length = total_length / len(articles)
        
        print(f"\n内容统计:")
        print(f"  总字符数: {total_length:,}")
        print(f"  平均长度: {avg_length:.0f} 字符/篇")
        
        # 保存
        output_path = 'backend/data/crawled/news_test.json'
        crawler.save_to_json(articles, output_path)
        
        # 显示示例
        print("\n" + "=" * 80)
        print("📰 文章示例:")
        print("=" * 80)
        for i, article in enumerate(articles[:3], 1):
            print(f"\n{i}. {article['title']}")
            print(f"   来源: {article['source']}")
            print(f"   日期: {article['published']}")
            print(f"   链接: {article['link']}")
            print(f"   摘要: {article['summary'][:100]}...")
        
        print("\n" + "=" * 80)
        print("✅ 测试完成！")
        print(f"保存位置: {output_path}")
        print("=" * 80)
    else:
        print("\n❌ 爬取失败，没有获取到数据")


if __name__ == '__main__':
    main()

