"""
验证完整薪资数据质量
Validate Full Salary Data Quality

Author: UniPulse Asia Team
Date: 2025-11-29
"""

import json
from pathlib import Path

def validate_full_salary_data():
    """验证完整薪资数据"""
    
    print("\n" + "="*70)
    print("🔍 完整薪资数据验证（150条）")
    print("="*70)
    
    # 读取数据
    filepath = Path("backend/data/crawled/salary_full.json")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    salaries = data['salaries']
    stats = data['stats']
    
    print(f"\n📦 数据规模：{stats['total_count']}条")
    print(f"   - 方案A（政府统计）：{stats['method_a_count']}条")
    print(f"   - 方案B（PayScale）：{stats['method_b_count']}条")
    print(f"   - 方案C（手动收集）：{stats['method_c_count']}条")
    
    # 验证必填字段
    required_fields = [
        'position', 'industry', 'salary_min', 'salary_max', 
        'currency', 'period', 'experience_level', 'location',
        'source', 'data_year', 'benefits', 'job_description',
        'required_skills', 'education', 'collection_method'
    ]
    
    validation_results = {
        'total_count': len(salaries),
        'valid_count': 0,
        'issues': []
    }
    
    print("\n✅ 数据完整性检查：")
    
    for idx, salary in enumerate(salaries, 1):
        is_valid = True
        
        # 检查必填字段
        for field in required_fields:
            if field not in salary or not salary[field]:
                validation_results['issues'].append(
                    f"职位{idx} 缺少字段：{field}"
                )
                is_valid = False
        
        # 检查薪资合理性
        if 'salary_min' in salary and 'salary_max' in salary:
            if salary['salary_min'] >= salary['salary_max']:
                validation_results['issues'].append(
                    f"职位{idx} ({salary.get('position', 'Unknown')}) 薪资范围不合理"
                )
                is_valid = False
        
        if is_valid:
            validation_results['valid_count'] += 1
    
    validity_score = (validation_results['valid_count'] / len(salaries)) * 100
    
    print(f"   ✅ 有效记录：{validation_results['valid_count']}/{len(salaries)} ({validity_score:.1f}%)")
    
    # 统计信息
    print("\n📊 数据覆盖：")
    print(f"   🏢 行业数量：{len(stats['industries'])}个")
    print(f"   📍 地区数量：{len(stats['locations'])}个")
    print(f"   💼 独特职位：{len(stats['positions'])}个")
    
    # 薪资范围分析
    avg_min = sum(s['salary_min'] for s in salaries) / len(salaries)
    avg_max = sum(s['salary_max'] for s in salaries) / len(salaries)
    print(f"\n💰 薪资范围：")
    print(f"   平均最低：MYR {avg_min:,.0f}/month")
    print(f"   平均最高：MYR {avg_max:,.0f}/month")
    
    # 显示问题（如果有）
    if validation_results['issues']:
        print(f"\n⚠️  发现 {len(validation_results['issues'])} 个问题")
        if len(validation_results['issues']) <= 5:
            for issue in validation_results['issues']:
                print(f"   - {issue}")
    else:
        print("\n✅ 未发现数据质量问题！")
    
    score = (validity_score / 10)
    
    print("="*70)
    print(f"📊 验证结果：{score:.1f}/10 ({'优秀' if score >= 9 else '良好' if score >= 8 else '需改进'})")
    print("="*70)
    
    return score >= 8.0


if __name__ == "__main__":
    success = validate_full_salary_data()
    
    if success:
        print("\n✅ 验证通过！数据质量优秀！可以进行正式导入。")
    else:
        print("\n⚠️  验证发现问题，请检查数据质量！")







