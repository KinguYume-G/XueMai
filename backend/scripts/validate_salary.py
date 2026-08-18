"""
验证薪资数据质量
Validate Salary Data Quality

Author: UniPulse Asia Team
Date: 2025-11-29
"""

import json
import os
from typing import Dict, List, Any

def validate_salary_data(filepath: str = "backend/data/crawled/salary_test.json") -> Dict[str, Any]:
    """验证薪资数据质量"""
    
    print("\n" + "="*70)
    print("🔍 薪资数据验证")
    print("="*70)
    
    # 读取数据
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
        'issues': [],
        'field_completeness': {},
        'salary_ranges': [],
        'industries': set(),
        'locations': set(),
        'experience_levels': set()
    }
    
    print("\n✅ 字段完整性检查：")
    for field in required_fields:
        count = sum(1 for s in salaries if field in s and s[field])
        completeness = (count / len(salaries)) * 100
        validation_results['field_completeness'][field] = completeness
        
        status = "✅" if completeness == 100 else "⚠️"
        print(f"   {status} {field}: {completeness:.1f}%")
    
    # 验证数据质量
    print("\n✅ 数据质量检查：")
    
    for idx, salary in enumerate(salaries, 1):
        is_valid = True
        
        # 检查必填字段
        for field in required_fields:
            if field not in salary or not salary[field]:
                validation_results['issues'].append(
                    f"职位{idx} ({salary.get('position', 'Unknown')}) 缺少字段：{field}"
                )
                is_valid = False
        
        # 检查薪资合理性
        if salary.get('salary_min') and salary.get('salary_max'):
            if salary['salary_min'] >= salary['salary_max']:
                validation_results['issues'].append(
                    f"职位{idx} ({salary['position']}) 薪资范围不合理"
                )
                is_valid = False
            else:
                validation_results['salary_ranges'].append({
                    'position': salary['position'],
                    'min': salary['salary_min'],
                    'max': salary['salary_max']
                })
        
        # 收集统计信息
        validation_results['industries'].add(salary.get('industry', 'Unknown'))
        validation_results['locations'].add(salary.get('location', 'Unknown'))
        validation_results['experience_levels'].add(salary.get('experience_level', 'Unknown'))
        
        if is_valid:
            validation_results['valid_count'] += 1
    
    # 计算验证分数
    completeness_score = sum(validation_results['field_completeness'].values()) / len(required_fields)
    validity_score = (validation_results['valid_count'] / len(salaries)) * 100
    overall_score = (completeness_score + validity_score) / 2
    
    print(f"   ✅ 完整性得分：{completeness_score:.1f}/100")
    print(f"   ✅ 有效记录：{validation_results['valid_count']}/{len(salaries)} ({validity_score:.1f}%)")
    print(f"   ✅ 综合得分：{overall_score:.1f}/100")
    
    # 统计信息
    print("\n📊 数据统计：")
    print(f"   🏢 覆盖行业：{len(validation_results['industries'])}个")
    print(f"   📍 覆盖地区：{len(validation_results['locations'])}个")
    print(f"   💼 经验等级：{len(validation_results['experience_levels'])}个")
    
    # 薪资范围分析
    if validation_results['salary_ranges']:
        avg_min = sum(s['min'] for s in validation_results['salary_ranges']) / len(validation_results['salary_ranges'])
        avg_max = sum(s['max'] for s in validation_results['salary_ranges']) / len(validation_results['salary_ranges'])
        print(f"\n💰 薪资范围分析：")
        print(f"   平均最低薪资：MYR {avg_min:,.0f}/month")
        print(f"   平均最高薪资：MYR {avg_max:,.0f}/month")
    
    # 显示问题（如果有）
    if validation_results['issues']:
        print(f"\n⚠️  发现 {len(validation_results['issues'])} 个问题：")
        for issue in validation_results['issues'][:5]:  # 只显示前5个
            print(f"   - {issue}")
    else:
        print("\n✅ 未发现数据质量问题！")
    
    print("="*70)
    print(f"📊 验证结果：{overall_score:.1f}/10 ({'优秀' if overall_score >= 90 else '良好' if overall_score >= 80 else '需改进'})")
    print("="*70)
    
    return {
        'score': overall_score / 10,  # 转换为10分制
        'valid_count': validation_results['valid_count'],
        'total_count': validation_results['total_count'],
        'issues': validation_results['issues'],
        'stats': {
            'industries': len(validation_results['industries']),
            'locations': len(validation_results['locations']),
            'experience_levels': len(validation_results['experience_levels'])
        }
    }


if __name__ == "__main__":
    result = validate_salary_data()
    
    if result['score'] >= 8.0:
        print("\n✅ 验证通过！数据质量优秀！")
    elif result['score'] >= 7.0:
        print("\n✅ 验证通过！数据质量良好！")
    else:
        print("\n⚠️  验证发现问题，请检查数据质量！")







