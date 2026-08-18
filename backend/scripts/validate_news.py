"""
新闻数据验证脚本
验证爬取的新闻数据质量
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from collections import Counter
import re


class NewsValidator:
    """新闻数据验证器"""
    
    def __init__(self):
        self.required_fields = ['title', 'summary', 'content', 'published', 'link', 'source']
        self.issues = []
        self.warnings = []
        
    def load_data(self, file_path: str) -> Tuple[bool, Dict]:
        """加载新闻数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'articles' in data:
                articles = data['articles']
                metadata = data.get('metadata', {})
            elif isinstance(data, list):
                articles = data
                metadata = {}
            else:
                self.issues.append("❌ 数据格式错误")
                return False, {}
            
            print(f"✅ 成功加载 {len(articles)} 篇新闻")
            return True, {'articles': articles, 'metadata': metadata}
            
        except Exception as e:
            self.issues.append(f"❌ 加载失败: {e}")
            return False, {}
    
    def validate_completeness(self, articles: List[Dict]) -> bool:
        """验证完整性"""
        print("\n1️⃣ 验证标题、摘要、正文完整性...")
        all_valid = True
        
        for i, article in enumerate(articles):
            # 检查必填字段
            missing = [f for f in self.required_fields if f not in article]
            if missing:
                self.issues.append(f"❌ 文章 {i+1} 缺少字段: {', '.join(missing)}")
                all_valid = False
                continue
            
            # 检查字段是否为空
            if not article.get('title') or len(article['title'].strip()) == 0:
                self.issues.append(f"❌ 文章 {i+1} 标题为空")
                all_valid = False
            
            if not article.get('summary') or len(article['summary'].strip()) == 0:
                self.warnings.append(f"⚠️  文章 {i+1} 摘要为空")
            
            if not article.get('content') or len(article['content'].strip()) < 50:
                self.warnings.append(f"⚠️  文章 {i+1} 正文过短: {len(article.get('content', ''))} 字符")
        
        if all_valid and not self.warnings:
            print(f"  ✅ 所有文章包含必填字段且内容完整")
        elif all_valid:
            print(f"  ⚡ 必填字段完整，但有 {len(self.warnings)} 个警告")
        
        return all_valid
    
    def validate_date_format(self, articles: List[Dict]) -> bool:
        """验证日期格式"""
        print("\n2️⃣ 验证日期格式...")
        
        date_formats = []
        invalid_count = 0
        
        for i, article in enumerate(articles):
            published = article.get('published', '')
            
            if not published:
                self.warnings.append(f"⚠️  文章 {i+1} 缺少发布日期")
                invalid_count += 1
                continue
            
            # 检测日期格式
            # RSS通常使用RFC 822格式：Fri, 28 Nov 2025 23:00:00 +0000
            if re.match(r'\w{3}, \d{2} \w{3} \d{4}', published):
                date_formats.append('RFC822')
            elif re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', published):
                date_formats.append('ISO8601')
            else:
                date_formats.append('Unknown')
                self.warnings.append(f"⚠️  文章 {i+1} 日期格式不标准: {published}")
        
        # 统计格式分布
        format_counts = Counter(date_formats)
        print(f"  日期格式分布:")
        for fmt, count in format_counts.items():
            print(f"    {fmt}: {count} 篇")
        
        if invalid_count == 0:
            print(f"  ✅ 所有文章包含发布日期")
        else:
            print(f"  ⚠️  {invalid_count} 篇文章缺少发布日期")
        
        return invalid_count == 0
    
    def validate_links(self, articles: List[Dict]) -> bool:
        """验证链接有效性"""
        print("\n3️⃣ 验证链接格式...")
        
        url_pattern = re.compile(r'^https?://')
        invalid_count = 0
        
        for i, article in enumerate(articles):
            link = article.get('link', '')
            
            if not link:
                self.issues.append(f"❌ 文章 {i+1} 缺少链接")
                invalid_count += 1
            elif not url_pattern.match(link):
                self.issues.append(f"❌ 文章 {i+1} 链接格式无效: {link}")
                invalid_count += 1
        
        if invalid_count == 0:
            print(f"  ✅ 所有链接格式正确")
        else:
            print(f"  ❌ {invalid_count} 个链接有问题")
        
        return invalid_count == 0
    
    def auto_fix(self, articles: List[Dict]) -> List[Dict]:
        """自动修复数据问题"""
        print("\n4️⃣ 自动修复问题...")
        fixed_count = 0
        
        for article in articles:
            # 如果content为空，使用summary
            if not article.get('content') or len(article['content'].strip()) < 50:
                if article.get('summary') and len(article['summary']) > 50:
                    article['content'] = article['summary']
                    fixed_count += 1
            
            # 统一日期格式为ISO8601
            published = article.get('published', '')
            if published and not re.match(r'\d{4}-\d{2}-\d{2}T', published):
                try:
                    # 尝试解析RFC822格式
                    from email.utils import parsedate_to_datetime
                    dt = parsedate_to_datetime(published)
                    article['published'] = dt.isoformat()
                    fixed_count += 1
                except:
                    pass
            
            # 确保有category
            if 'category' not in article:
                article['category'] = 'startup'
                fixed_count += 1
            
            # 确保有subcategory
            if 'subcategory' not in article:
                article['subcategory'] = 'news'
                fixed_count += 1
        
        if fixed_count > 0:
            print(f"  🔧 自动修复了 {fixed_count} 个问题")
        else:
            print(f"  ℹ️  没有需要修复的问题")
        
        return articles
    
    def calculate_quality_score(self, articles: List[Dict]) -> float:
        """计算质量评分"""
        total_score = 10.0
        
        # 根据问题扣分
        total_score -= len(self.issues) * 0.5
        total_score -= len(self.warnings) * 0.1
        
        return max(0.0, min(10.0, total_score))
    
    def save_fixed_data(self, data: Dict, file_path: str):
        """保存修复后的数据"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\n✅ 修复后的数据已保存")
        except Exception as e:
            print(f"\n❌ 保存失败: {e}")
    
    def generate_report(self, score: float, articles: List[Dict]):
        """生成验证报告"""
        print("\n" + "=" * 80)
        print("📊 新闻数据质量报告")
        print("=" * 80)
        
        print(f"\n数据统计:")
        print(f"  - 文章总数: {len(articles)}")
        print(f"  - 平均内容长度: {sum(a.get('content_length', 0) for a in articles) / len(articles):.0f} 字符")
        
        # 来源统计
        sources = Counter(a.get('source', 'Unknown') for a in articles)
        print(f"  - 来源分布:")
        for source, count in sources.items():
            print(f"    {source}: {count} 篇")
        
        print(f"\n验证结果:")
        if not self.issues:
            print("  ✅ 没有发现严重问题")
        else:
            print(f"  ❌ 发现 {len(self.issues)} 个问题:")
            for issue in self.issues[:5]:
                print(f"    {issue}")
        
        if self.warnings:
            print(f"\n  ⚠️  {len(self.warnings)} 个警告:")
            for warning in self.warnings[:5]:
                print(f"    {warning}")
        
        print(f"\n数据质量评分: {score:.1f}/10.0")
        
        if score >= 8.0:
            print("  ✅ 优秀 - 可以直接使用")
            status = "PASS"
        elif score >= 6.0:
            print("  ⚡ 良好 - 建议修复后使用")
            status = "PASS_WITH_WARNINGS"
        else:
            print("  ❌ 不合格 - 需要重新爬取")
            status = "FAIL"
        
        print("=" * 80)
        
        return status


def main():
    """主函数"""
    print("=" * 80)
    print("🔍 新闻数据验证")
    print("=" * 80)
    
    # 文件路径
    file_path = Path(__file__).parent.parent / 'backend' / 'data' / 'crawled' / 'news_test.json'
    
    print(f"\n验证文件: {file_path}")
    
    # 创建验证器
    validator = NewsValidator()
    
    # 1. 加载数据
    success, data = validator.load_data(str(file_path))
    if not success:
        print("\n❌ 验证失败")
        sys.exit(1)
    
    articles = data['articles']
    
    # 2. 验证完整性
    validator.validate_completeness(articles)
    
    # 3. 验证日期格式
    validator.validate_date_format(articles)
    
    # 4. 验证链接
    validator.validate_links(articles)
    
    # 5. 自动修复
    fixed_articles = validator.auto_fix(articles)
    
    # 6. 计算质量评分
    score = validator.calculate_quality_score(fixed_articles)
    
    # 7. 保存修复后的数据
    data['articles'] = fixed_articles
    validator.save_fixed_data(data, str(file_path))
    
    # 8. 生成报告
    status = validator.generate_report(score, fixed_articles)
    
    # 9. 返回结果
    if status == "PASS" or status == "PASS_WITH_WARNINGS":
        print("\n✅ 验收通过！新闻数据质量良好")
        sys.exit(0)
    else:
        print("\n❌ 验收失败！")
        sys.exit(1)


if __name__ == '__main__':
    main()

