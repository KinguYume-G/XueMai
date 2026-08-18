"""
Academic Resources Crawler
爬取学术写作和引用格式资源
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime

from bs4 import BeautifulSoup

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from base_crawler import BaseCrawler


class AcademicCrawler(BaseCrawler):
    """学术资源爬虫"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def scrape(self, urls: List[str] = None) -> List[Dict]:
        """
        爬取学术资源
        
        Args:
            urls: 要爬取的URL列表，如果为None则使用默认URL
            
        Returns:
            爬取的数据列表
        """
        if urls is None:
            # 默认：Purdue OWL APA引用格式页面
            urls = [
                'https://owl.purdue.edu/owl/research_and_citation/apa_style/apa_formatting_and_style_guide/general_format.html'
            ]
        
        results = []
        
        for url in urls:
            self.logger.info(f"开始爬取: {url}")
            
            # 检查robots.txt
            if not self.check_robots_txt(url):
                self.logger.warning(f"跳过（robots.txt禁止）: {url}")
                continue
            
            # 获取页面
            html = self.fetch_page(url)
            if not html:
                self.logger.error(f"跳过（获取失败）: {url}")
                continue
            
            # 解析页面
            soup = self.parse_html(html)
            if not soup:
                self.logger.error(f"跳过（解析失败）: {url}")
                continue
            
            # 提取数据
            data = self.parse_page(soup, url)
            if data:
                results.append(data)
                self.logger.info(f"✅ 成功提取数据: {data['title']}")
            else:
                self.logger.error(f"跳过（数据提取失败）: {url}")
        
        self.logger.info(f"爬取完成，共获取 {len(results)} 条数据")
        return results
    
    def parse_page(self, soup: BeautifulSoup, url: str) -> Dict:
        """
        解析Purdue OWL页面
        
        Args:
            soup: BeautifulSoup对象
            url: 页面URL
            
        Returns:
            结构化数据
        """
        try:
            # 提取标题
            title = None
            
            # 尝试多种标题选择器
            title_selectors = [
                'h1',
                'h1.page-title',
                'title',
                '.entry-title'
            ]
            
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    break
            
            if not title:
                title = "Untitled Page"
            
            # 提取主要内容
            content = ""
            
            # Purdue OWL的内容通常在 #main-content 或 .content 中
            content_selectors = [
                '#main-content',
                '#content',
                '.content',
                'main',
                'article'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # 移除脚本和样式
                    for script in content_elem(['script', 'style', 'nav', 'footer', 'header']):
                        script.decompose()
                    
                    # 提取文本，保留段落结构
                    paragraphs = []
                    for p in content_elem.find_all(['p', 'h2', 'h3', 'h4', 'li']):
                        text = p.get_text(strip=True)
                        if text:
                            paragraphs.append(text)
                    
                    content = '\n\n'.join(paragraphs)
                    break
            
            if not content:
                # 如果找不到特定容器，提取所有段落
                paragraphs = [p.get_text(strip=True) for p in soup.find_all('p') if p.get_text(strip=True)]
                content = '\n\n'.join(paragraphs)
            
            # 清理内容
            content = self._clean_content(content)
            
            # 构建数据字典
            data = {
                'title': title,
                'content': content,
                'source_url': url,
                'category': 'academic',
                'subcategory': 'citation',
                'scraped_at': datetime.now().isoformat(),
                'content_length': len(content),
                'word_count': len(content.split())
            }
            
            self.logger.info(f"提取内容: {len(content)}字符, {len(content.split())}词")
            
            return data
            
        except Exception as e:
            self.logger.error(f"解析页面失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _clean_content(self, content: str) -> str:
        """清理内容"""
        # 移除多余的空白
        lines = [line.strip() for line in content.split('\n')]
        lines = [line for line in lines if line]
        
        # 重新组合
        cleaned = '\n\n'.join(lines)
        
        return cleaned
    
    def save_to_json(self, data: List[Dict], output_path: str):
        """
        保存数据到JSON文件
        
        Args:
            data: 要保存的数据
            output_path: 输出文件路径
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"✅ 数据已保存到: {output_path}")
            self.logger.info(f"文件大小: {output_file.stat().st_size / 1024:.2f} KB")
            
        except Exception as e:
            self.logger.error(f"❌ 保存失败: {e}")


def main():
    """主函数：执行测试爬虫"""
    print("=" * 80)
    print("🕷️  学术资源爬虫 - 测试运行")
    print("=" * 80)
    
    # 配置
    config = {
        'rate_limit': 2,  # 2秒延迟
        'timeout': 10
    }
    
    # 创建爬虫实例
    crawler = AcademicCrawler(config)
    
    # 执行爬取
    print("\n正在爬取Purdue OWL APA引用格式页面...")
    results = crawler.scrape()
    
    # 保存结果
    if results:
        output_path = 'backend/data/crawled/academic_test.json'
        crawler.save_to_json(results, output_path)
        
        print("\n" + "=" * 80)
        print("✅ 爬取成功！")
        print("=" * 80)
        print(f"爬取数量: {len(results)} 页")
        print(f"保存位置: {output_path}")
        print("\n数据摘要:")
        for i, item in enumerate(results, 1):
            print(f"\n{i}. {item['title']}")
            print(f"   URL: {item['source_url']}")
            print(f"   内容长度: {item['content_length']} 字符")
            print(f"   词数: {item['word_count']} 词")
            print(f"   爬取时间: {item['scraped_at']}")
        print("=" * 80)
    else:
        print("\n❌ 爬取失败，没有获取到数据")


if __name__ == '__main__':
    main()

