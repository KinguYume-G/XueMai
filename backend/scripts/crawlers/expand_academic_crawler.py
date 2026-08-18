"""
扩展学术资源爬虫 - 爬取完整引用格式指南
目标：APA、MLA、Chicago、IEEE格式完整指南
"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from academic_crawler import AcademicCrawler


def main():
    """爬取完整的引用格式指南"""
    print("=" * 80)
    print("📚 扩展学术资源爬虫 - 完整引用格式指南")
    print("=" * 80)
    
    # 配置
    config = {
        'rate_limit': 3,  # 3秒延迟，更谨慎
        'timeout': 15
    }
    
    # 创建爬虫
    crawler = AcademicCrawler(config)
    
    # 定义要爬取的URL
    urls = {
        'APA格式': [
            'https://owl.purdue.edu/owl/research_and_citation/apa_style/apa_formatting_and_style_guide/general_format.html',
            'https://owl.purdue.edu/owl/research_and_citation/apa_style/apa_formatting_and_style_guide/in_text_citations_the_basics.html',
            'https://owl.purdue.edu/owl/research_and_citation/apa_style/apa_formatting_and_style_guide/reference_list_basic_rules.html',
            'https://owl.purdue.edu/owl/research_and_citation/apa_style/apa_formatting_and_style_guide/reference_list_books.html',
            'https://owl.purdue.edu/owl/research_and_citation/apa_style/apa_formatting_and_style_guide/reference_list_articles_in_periodicals.html',
            'https://owl.purdue.edu/owl/research_and_citation/apa_style/apa_formatting_and_style_guide/reference_list_electronic_sources.html',
        ],
        'MLA格式': [
            'https://owl.purdue.edu/owl/research_and_citation/mla_style/mla_formatting_and_style_guide/mla_formatting_and_style_guide.html',
            'https://owl.purdue.edu/owl/research_and_citation/mla_style/mla_formatting_and_style_guide/mla_in_text_citations_the_basics.html',
            'https://owl.purdue.edu/owl/research_and_citation/mla_style/mla_formatting_and_style_guide/mla_works_cited_page_basic_format.html',
            'https://owl.purdue.edu/owl/research_and_citation/mla_style/mla_formatting_and_style_guide/mla_works_cited_electronic_sources.html',
        ],
        'Chicago格式': [
            'https://owl.purdue.edu/owl/research_and_citation/chicago_manual_17th_edition/cmos_formatting_and_style_guide/chicago_manual_of_style_17th_edition.html',
            'https://owl.purdue.edu/owl/research_and_citation/chicago_manual_17th_edition/cmos_formatting_and_style_guide/chicago_footnotes_and_endnotes.html',
            'https://owl.purdue.edu/owl/research_and_citation/chicago_manual_17th_edition/cmos_formatting_and_style_guide/chicago_bibliography.html',
        ],
        'IEEE格式': [
            'https://owl.purdue.edu/owl/research_and_citation/ieee_style/ieee_overview.html',
            'https://owl.purdue.edu/owl/research_and_citation/ieee_style/ieee_in_text_and_reference_list.html',
        ],
    }
    
    # 爬取所有URL
    all_results = []
    
    for category, url_list in urls.items():
        print(f"\n{'='*80}")
        print(f"📖 开始爬取：{category} ({len(url_list)}个页面)")
        print(f"{'='*80}\n")
        
        results = crawler.scrape(url_list)
        
        # 为每个结果添加分类标签
        for result in results:
            result['subcategory'] = category.lower().replace('格式', '_format')
            all_results.append(result)
        
        print(f"\n✅ {category}爬取完成：{len(results)}/{len(url_list)}个页面")
    
    # 保存结果
    print(f"\n{'='*80}")
    print(f"📊 爬取统计")
    print(f"{'='*80}")
    print(f"总页面数：{len(all_results)}")
    print(f"总字符数：{sum(r['content_length'] for r in all_results):,}")
    print(f"总词数：{sum(r['word_count'] for r in all_results):,}")
    
    # 按类别统计
    print(f"\n按类别统计：")
    for category in urls.keys():
        category_results = [r for r in all_results if category.lower().replace('格式', '_format') in r.get('subcategory', '')]
        print(f"  {category}: {len(category_results)} 个页面")
    
    # 保存为JSON
    output_path = 'backend/data/crawled/academic_full.json'
    crawler.save_to_json(all_results, output_path)
    
    print(f"\n{'='*80}")
    print(f"✅ 爬取完成！")
    print(f"保存位置：{output_path}")
    print(f"总数据量：{len(all_results)} 条")
    print(f"{'='*80}")
    
    return all_results


if __name__ == '__main__':
    results = main()

