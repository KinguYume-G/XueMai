"""
生成完整项目数据统计报告
Generate Final Project Data Statistics Report

统计Round 1, Round 2, Round 3的所有数据

Author: UniPulse Asia Team
Date: 2025-11-29
"""

import os
import sys
import django
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Django setup
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.ai.models import AIDocument, AIChunk, AIEmbedding


def generate_final_statistics():
    """生成最终数据统计"""
    
    print("\n" + "="*80)
    print("📊 UniPulse Asia RAG 数据采集 - 最终统计报告")
    print("="*80)
    print(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 获取所有数据
    all_docs = AIDocument.objects.all()
    all_chunks = AIChunk.objects.all()
    all_embeddings = AIEmbedding.objects.all()
    
    total_docs = all_docs.count()
    total_chunks = all_chunks.count()
    total_embeddings = all_embeddings.count()
    
    print(f"\n🎯 总体数据规模：")
    print(f"   📄 文档总数：{total_docs:,}")
    print(f"   📦 Chunks总数：{total_chunks:,}")
    print(f"   🔢 Embeddings总数：{total_embeddings:,}")
    print(f"   ✅ 数据完整性：{'100%' if total_chunks == total_embeddings else f'{(total_embeddings/total_chunks*100):.1f}%'}")
    
    # Round 1 统计（学术、面试、创业新闻）
    print("\n" + "-"*80)
    print("📅 Round 1 数据统计")
    print("-"*80)
    
    # 根据doc_type和metadata统计Round 1
    # Round 1包含：academic（学术资源）、interview（面试题）、其他历史数据
    round1_docs = AIDocument.objects.filter(
        doc_type__in=['course', 'regulation', 'announcement', 'post', 'other']
    ).exclude(
        metadata__data_type__in=['resume_template', 'business_plan', 'company_info', 'market_report', 'salary']
    )
    
    # 更精确地获取Round1数据（排除Round2数据）
    round1_count = 0
    round1_chunks_count = 0
    round1_embeddings_count = 0
    
    # 检查academic数据
    academic_docs = AIDocument.objects.filter(doc_type='other', metadata__category='academic').count()
    if academic_docs > 0:
        academic_chunks = AIChunk.objects.filter(document__doc_type='other', document__metadata__category='academic').count()
        academic_embeddings = AIEmbedding.objects.filter(chunk__document__doc_type='other', chunk__document__metadata__category='academic').count()
        print(f"   📚 学术资源：{academic_docs} 文档, {academic_chunks} chunks, {academic_embeddings} embeddings")
        round1_count += academic_docs
        round1_chunks_count += academic_chunks
        round1_embeddings_count += academic_embeddings
    
    # 检查interview数据
    interview_docs = AIDocument.objects.filter(doc_type='other', metadata__category='interview').count()
    if interview_docs > 0:
        interview_chunks = AIChunk.objects.filter(document__doc_type='other', document__metadata__category='interview').count()
        interview_embeddings = AIEmbedding.objects.filter(chunk__document__doc_type='other', chunk__document__metadata__category='interview').count()
        print(f"   💼 面试题库：{interview_docs} 文档, {interview_chunks} chunks, {interview_embeddings} embeddings")
        round1_count += interview_docs
        round1_chunks_count += interview_chunks
        round1_embeddings_count += interview_embeddings
    
    # 检查news数据
    news_docs = AIDocument.objects.filter(doc_type='other', metadata__category='startup_news').count()
    if news_docs > 0:
        news_chunks = AIChunk.objects.filter(document__doc_type='other', document__metadata__category='startup_news').count()
        news_embeddings = AIEmbedding.objects.filter(chunk__document__doc_type='other', chunk__document__metadata__category='startup_news').count()
        print(f"   🚀 创业新闻：{news_docs} 文档, {news_chunks} chunks, {news_embeddings} embeddings")
        round1_count += news_docs
        round1_chunks_count += news_chunks
        round1_embeddings_count += news_embeddings
    
    # APU数据
    apu_docs = round1_docs.exclude(metadata__category__in=['academic', 'interview', 'startup_news']).count()
    if apu_docs > 0:
        apu_chunks = AIChunk.objects.filter(
            document__in=round1_docs.exclude(metadata__category__in=['academic', 'interview', 'startup_news'])
        ).count()
        apu_embeddings = AIEmbedding.objects.filter(
            chunk__in=AIChunk.objects.filter(
                document__in=round1_docs.exclude(metadata__category__in=['academic', 'interview', 'startup_news'])
            )
        ).count()
        print(f"   🎓 APU相关数据：{apu_docs} 文档, {apu_chunks} chunks, {apu_embeddings} embeddings")
        round1_count += apu_docs
        round1_chunks_count += apu_chunks
        round1_embeddings_count += apu_embeddings
    
    round1_chunks = round1_chunks_count
    round1_embeddings = round1_embeddings_count
    print(f"   📊 Round 1 小计：{round1_count} 文档, {round1_chunks} chunks")
    
    # Round 2 统计（简历、BP、公司、市场报告）
    print("\n" + "-"*80)
    print("📅 Round 2 数据统计")
    print("-"*80)
    
    # 简历模板
    resume_docs = AIDocument.objects.filter(metadata__import_source='resume_full').count()
    resume_chunks = AIChunk.objects.filter(chunk_metadata__source='resume_full').count()
    resume_embeddings = AIEmbedding.objects.filter(chunk__chunk_metadata__source='resume_full').count()
    print(f"   📄 简历模板：{resume_docs} 文档, {resume_chunks} chunks, {resume_embeddings} embeddings")
    
    # BP模板
    bp_docs = AIDocument.objects.filter(metadata__import_source='bp_full').count()
    bp_chunks = AIChunk.objects.filter(chunk_metadata__source='bp_full').count()
    bp_embeddings = AIEmbedding.objects.filter(chunk__chunk_metadata__source='bp_full').count()
    print(f"   📋 BP模板：{bp_docs} 文档, {bp_chunks} chunks, {bp_embeddings} embeddings")
    
    # 公司信息
    company_docs = AIDocument.objects.filter(metadata__import_source='company_full').count()
    company_chunks = AIChunk.objects.filter(chunk_metadata__source='company_full').count()
    company_embeddings = AIEmbedding.objects.filter(chunk__chunk_metadata__source='company_full').count()
    print(f"   🏢 公司信息：{company_docs} 文档, {company_chunks} chunks, {company_embeddings} embeddings")
    
    # 市场报告
    market_docs = AIDocument.objects.filter(metadata__import_source='market_full').count()
    market_chunks = AIChunk.objects.filter(chunk_metadata__source='market_full').count()
    market_embeddings = AIEmbedding.objects.filter(chunk__chunk_metadata__source='market_full').count()
    print(f"   📊 市场报告：{market_docs} 文档, {market_chunks} chunks, {market_embeddings} embeddings")
    
    round2_count = resume_docs + bp_docs + company_docs + market_docs
    round2_chunks = resume_chunks + bp_chunks + company_chunks + market_chunks
    round2_embeddings = resume_embeddings + bp_embeddings + company_embeddings + market_embeddings
    print(f"   📊 Round 2 小计：{round2_count} 文档, {round2_chunks} chunks")
    
    # Round 3 统计（薪资数据）
    print("\n" + "-"*80)
    print("📅 Round 3 数据统计")
    print("-"*80)
    
    # 薪资数据
    salary_docs = AIDocument.objects.filter(metadata__import_source='salary_full').count()
    salary_chunks = AIChunk.objects.filter(chunk_metadata__source='salary_full').count()
    salary_embeddings = AIEmbedding.objects.filter(chunk__chunk_metadata__source='salary_full').count()
    print(f"   💰 薪资数据：{salary_docs} 文档, {salary_chunks} chunks, {salary_embeddings} embeddings")
    
    round3_count = salary_docs
    round3_chunks = salary_chunks
    round3_embeddings = salary_embeddings
    print(f"   📊 Round 3 小计：{round3_count} 文档, {round3_chunks} chunks")
    
    # 汇总统计
    print("\n" + "="*80)
    print("📈 数据汇总统计")
    print("="*80)
    
    print(f"\n按Round统计：")
    print(f"   Round 1：{round1_count:>4} 文档  |  {round1_chunks:>5} chunks  |  {round1_embeddings:>5} embeddings")
    print(f"   Round 2：{round2_count:>4} 文档  |  {round2_chunks:>5} chunks  |  {round2_embeddings:>5} embeddings")
    print(f"   Round 3：{round3_count:>4} 文档  |  {round3_chunks:>5} chunks  |  {round3_embeddings:>5} embeddings")
    print(f"   " + "-"*70)
    print(f"   总计：    {round1_count + round2_count + round3_count:>4} 文档  |  {round1_chunks + round2_chunks + round3_chunks:>5} chunks  |  {round1_embeddings + round2_embeddings + round3_embeddings:>5} embeddings")
    
    # AI功能统计
    print(f"\n✨ AI功能覆盖：")
    print(f"   1. ✅ APU信息查询 (Round 1)")
    print(f"   2. ✅ 学术写作AI (Round 1)")
    print(f"   3. ✅ Career AI - 面试准备 (Round 1)")
    print(f"   4. ✅ Startup AI - 创业新闻 (Round 1)")
    print(f"   5. ✅ Career AI - 简历优化 (Round 2 - {resume_docs}个模板)")
    print(f"   6. ✅ Startup AI - BP写作 (Round 2 - {bp_docs}个模板)")
    print(f"   7. ✅ Career AI - 公司推荐 (Round 2 - {company_docs}家公司)")
    print(f"   8. ✅ Startup AI - 市场分析 (Round 2 - {market_docs}篇报告)")
    print(f"   9. ✅ Career AI - 薪资查询 (Round 3 - {salary_docs}个职位) 🆕")
    print(f"\n   🎯 总计：9个完整的AI辅助功能")
    
    # 数据质量
    print(f"\n📊 数据质量：")
    integrity_rate = (total_embeddings / total_chunks * 100) if total_chunks > 0 else 0
    print(f"   数据完整性：{integrity_rate:.2f}% (chunks vs embeddings)")
    print(f"   平均chunks/文档：{total_chunks / total_docs:.1f}")
    
    print("\n" + "="*80)
    print("✅ 数据统计报告生成完成！")
    print("="*80)
    
    # 保存报告
    report_file = Path(__file__).parent.parent / 'docs' / 'FINAL_DATA_STATISTICS.md'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"# UniPulse Asia RAG 数据采集 - 最终统计报告\n\n")
        f.write(f"**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"---\n\n")
        
        f.write(f"## 🎯 总体数据规模\n\n")
        f.write(f"| 指标 | 数量 |\n")
        f.write(f"|------|------|\n")
        f.write(f"| 📄 文档总数 | {total_docs:,} |\n")
        f.write(f"| 📦 Chunks总数 | {total_chunks:,} |\n")
        f.write(f"| 🔢 Embeddings总数 | {total_embeddings:,} |\n")
        f.write(f"| ✅ 数据完整性 | {integrity_rate:.2f}% |\n\n")
        
        f.write(f"---\n\n")
        f.write(f"## 📅 分Round统计\n\n")
        
        f.write(f"### Round 1 数据\n\n")
        f.write(f"| 数据源 | 文档数 | Chunks | Embeddings |\n")
        f.write(f"|--------|--------|--------|------------|\n")
        if academic_docs > 0:
            f.write(f"| 📚 学术资源 | {academic_docs} | {academic_chunks} | {academic_embeddings} |\n")
        if interview_docs > 0:
            f.write(f"| 💼 面试题库 | {interview_docs} | {interview_chunks} | {interview_embeddings} |\n")
        if news_docs > 0:
            f.write(f"| 🚀 创业新闻 | {news_docs} | {news_chunks} | {news_embeddings} |\n")
        if apu_docs > 0:
            f.write(f"| 🎓 APU相关 | {apu_docs} | {apu_chunks} | {apu_embeddings} |\n")
        f.write(f"| **小计** | **{round1_count}** | **{round1_chunks}** | **{round1_embeddings}** |\n\n")
        
        f.write(f"### Round 2 数据\n\n")
        f.write(f"| 数据源 | 文档数 | Chunks | Embeddings |\n")
        f.write(f"|--------|--------|--------|------------|\n")
        f.write(f"| 📄 简历模板 | {resume_docs} | {resume_chunks} | {resume_embeddings} |\n")
        f.write(f"| 📋 BP模板 | {bp_docs} | {bp_chunks} | {bp_embeddings} |\n")
        f.write(f"| 🏢 公司信息 | {company_docs} | {company_chunks} | {company_embeddings} |\n")
        f.write(f"| 📊 市场报告 | {market_docs} | {market_chunks} | {market_embeddings} |\n")
        f.write(f"| **小计** | **{round2_count}** | **{round2_chunks}** | **{round2_embeddings}** |\n\n")
        
        f.write(f"### Round 3 数据\n\n")
        f.write(f"| 数据源 | 文档数 | Chunks | Embeddings |\n")
        f.write(f"|--------|--------|--------|------------|\n")
        f.write(f"| 💰 薪资数据 | {salary_docs} | {salary_chunks} | {salary_embeddings} |\n")
        f.write(f"| **小计** | **{round3_count}** | **{round3_chunks}** | **{round3_embeddings}** |\n\n")
        
        f.write(f"---\n\n")
        f.write(f"## ✨ AI功能覆盖\n\n")
        f.write(f"UniPulse Asia现在支持**9个完整的AI辅助功能**：\n\n")
        f.write(f"**Round 1功能（4个）：**\n")
        f.write(f"1. ✅ APU信息查询\n")
        f.write(f"2. ✅ 学术写作AI\n")
        f.write(f"3. ✅ Career AI - 面试准备\n")
        f.write(f"4. ✅ Startup AI - 创业新闻\n\n")
        f.write(f"**Round 2功能（4个）：**\n")
        f.write(f"5. ✅ Career AI - 简历优化（{resume_docs}个模板）\n")
        f.write(f"6. ✅ Startup AI - BP写作（{bp_docs}个模板）\n")
        f.write(f"7. ✅ Career AI - 公司推荐（{company_docs}家公司）\n")
        f.write(f"8. ✅ Startup AI - 市场分析（{market_docs}篇报告）\n\n")
        f.write(f"**Round 3功能（1个）：**\n")
        f.write(f"9. ✅ Career AI - 薪资查询（{salary_docs}个职位）🆕\n\n")
        
        f.write(f"---\n\n")
        f.write(f"## 📊 数据质量\n\n")
        f.write(f"- **数据完整性：** {integrity_rate:.2f}%\n")
        f.write(f"- **平均chunks/文档：** {total_chunks / total_docs:.1f}\n\n")
        
        f.write(f"---\n\n")
        f.write(f"**报告生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**状态：** ✅ 完成\n")
    
    print(f"\n💾 报告已保存到：{report_file}")
    
    return True


if __name__ == "__main__":
    generate_final_statistics()

