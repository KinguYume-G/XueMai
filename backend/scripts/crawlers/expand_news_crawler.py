"""
扩展新闻爬虫 - 多数据源
爬取TechCrunch、e27、Tech in Asia等多个创业新闻源
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent))
from news_crawler import NewsCrawler


class ExpandedNewsCrawler:
    """扩展的创业新闻爬虫 - 多数据源"""
    
    def __init__(self):
        self.crawler = NewsCrawler({'rate_limit': 3, 'timeout': 15})
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 多个RSS源
        self.rss_feeds = {
            'TechCrunch': 'https://techcrunch.com/feed/',
            'TechCrunch Startups': 'https://techcrunch.com/category/startups/feed/',
            'VentureBeat': 'https://venturebeat.com/feed/',
            # e27和Tech in Asia的RSS需要确认
        }
    
    def scrape_all_sources(self, articles_per_source: int = 35) -> List[Dict]:
        """
        从所有RSS源爬取新闻
        
        Args:
            articles_per_source: 每个源的文章数量
            
        Returns:
            所有文章列表
        """
        print("=" * 80)
        print("📰 扩展新闻爬虫 - 多数据源爬取")
        print("=" * 80)
        
        all_articles = []
        
        for source_name, rss_url in self.rss_feeds.items():
            print(f"\n🔍 爬取: {source_name}")
            print(f"   RSS: {rss_url}")
            
            try:
                articles = self.crawler.scrape_rss(rss_url, max_items=articles_per_source)
                
                if articles:
                    all_articles.extend(articles)
                    print(f"   ✅ 获取 {len(articles)} 篇文章")
                else:
                    print(f"   ⚠️  未获取到文章")
                    
            except Exception as e:
                print(f"   ❌ 失败: {e}")
        
        # 去重（基于链接）
        seen_links = set()
        unique_articles = []
        
        for article in all_articles:
            link = article.get('link', '')
            if link and link not in seen_links:
                seen_links.add(link)
                unique_articles.append(article)
        
        removed = len(all_articles) - len(unique_articles)
        if removed > 0:
            print(f"\n🔧 去重：移除 {removed} 篇重复文章")
        
        print(f"\n✅ 总计获取 {len(unique_articles)} 篇独特文章")
        
        return unique_articles
    
    def save_articles(self, articles: List[Dict], output_path: str):
        """保存文章到JSON"""
        self.crawler.save_to_json(articles, output_path)


def main():
    """主函数"""
    print("=" * 80)
    print("📰 扩展创业新闻爬虫")
    print("=" * 80)
    
    crawler = ExpandedNewsCrawler()
    
    # 爬取所有源（目标100篇，每源35篇）
    articles = crawler.scrape_all_sources(articles_per_source=35)
    
    if len(articles) >= 100:
        # 只保留前100篇
        articles = articles[:100]
        print(f"\n✂️  截取前100篇文章")
    
    # 统计
    print(f"\n" + "=" * 80)
    print("📊 数据统计")
    print("=" * 80)
    
    if articles:
        from collections import Counter
        
        sources = Counter(a.get('source', 'Unknown') for a in articles)
        
        print(f"\n文章总数: {len(articles)}")
        print(f"\n来源分布:")
        for source, count in sources.items():
            print(f"  {source}: {count} 篇")
        
        total_length = sum(a.get('content_length', 0) for a in articles)
        avg_length = total_length / len(articles)
        print(f"\n内容统计:")
        print(f"  总字符数: {total_length:,}")
        print(f"  平均长度: {avg_length:.0f} 字符/篇")
        
        # 保存
        output_path = 'backend/backend/data/crawled/news_full.json'
        crawler.save_articles(articles, output_path)
        
        print(f"\n" + "=" * 80)
        print("✅ 扩展爬取完成！")
        print(f"保存位置: {output_path}")
        print("=" * 80)
    else:
        print("\n❌ 爬取失败，没有获取到数据")


if __name__ == '__main__':
    main()

