"""
公司信息数据验证脚本
验证公司信息的数据质量
"""

import json
from pathlib import Path
from typing import Dict, List
import sys


class CompanyDataValidator:
    """公司数据验证器"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.companies = []
        self.validation_results = {
            'total_score': 0,
            'max_score': 10,
            'checks': []
        }
    
    def load_data(self):
        """加载数据"""
        print(f"加载数据: {self.file_path}")
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.companies = data.get('companies', data if isinstance(data, list) else [])
        print(f"✅ 加载了 {len(self.companies)} 家公司\n")
    
    def check_completeness(self) -> bool:
        """检查1：数据完整性（必填字段）"""
        print("检查1：数据完整性")
        print("-" * 60)
        
        required_fields = ['company_name', 'industry', 'size', 'location', 'description', 'source']
        score = 2
        
        for i, company in enumerate(self.companies):
            missing = [field for field in required_fields if not company.get(field)]
            
            if missing:
                print(f"  ❌ 公司 {i+1}: 缺少字段 {missing}")
                score = 0
            else:
                print(f"  ✅ 公司 {i+1} ({company['company_name'][:30]}...): 所有字段完整")
        
        self.validation_results['checks'].append({
            'name': '数据完整性',
            'score': score,
            'max': 2,
            'passed': score == 2
        })
        
        print(f"\n得分: {score}/2\n")
        return score == 2
    
    def check_content_quality(self) -> bool:
        """检查2：内容质量"""
        print("检查2：内容质量")
        print("-" * 60)
        
        score = 3
        issues = []
        
        for i, company in enumerate(self.companies):
            company_name = company.get('company_name', 'Unknown')
            description = company.get('description', '')
            
            # 检查描述长度
            if len(description) < 100:
                issues.append(f"公司 {i+1} ({company_name}): 描述过短 ({len(description)}字符)")
                score -= 0.2
            else:
                print(f"  ✅ 公司 {i+1} ({company_name[:30]}...): 描述充足 ({len(description)}字符)")
        
        if issues:
            print("\n  问题:")
            for issue in issues:
                print(f"    ⚠️  {issue}")
        
        score = max(0, score)
        
        self.validation_results['checks'].append({
            'name': '内容质量',
            'score': score,
            'max': 3,
            'passed': score >= 2.5
        })
        
        print(f"\n得分: {score:.1f}/3\n")
        return score >= 2.5
    
    def check_category_accuracy(self) -> bool:
        """检查3：分类准确性"""
        print("检查3：分类准确性")
        print("-" * 60)
        
        score = 2
        
        valid_industries = ['Technology', 'E-commerce', 'Fintech', 'Manufacturing', 
                          'Professional Services', 'Healthcare', 'Construction', 
                          'Conglomerate', 'F&B', 'Energy']
        
        for i, company in enumerate(self.companies):
            company_name = company.get('company_name', 'Unknown')
            industry = company.get('industry', '')
            size = company.get('size', '')
            location = company.get('location', '')
            
            # 检查行业
            if not any(valid in industry for valid in valid_industries):
                print(f"  ⚠️  公司 {i+1}: 行业标签不标准 ({industry})")
                score -= 0.2
            else:
                print(f"  ✅ 公司 {i+1} ({company_name[:30]}...): 行业={industry}")
            
            # 检查规模
            if 'employee' not in size.lower():
                print(f"  ⚠️  公司 {i+1}: 规模格式不标准 ({size})")
                score -= 0.1
            
            # 检查地点
            if 'Malaysia' not in location:
                print(f"  ⚠️  公司 {i+1}: 地点需包含Malaysia ({location})")
                score -= 0.1
        
        score = max(0, score)
        
        self.validation_results['checks'].append({
            'name': '分类准确性',
            'score': score,
            'max': 2,
            'passed': score >= 1.5
        })
        
        print(f"\n得分: {score:.1f}/2\n")
        return score >= 1.5
    
    def check_duplicates(self) -> bool:
        """检查4：去重"""
        print("检查4：重复检测")
        print("-" * 60)
        
        score = 2
        
        names = [c.get('company_name', '') for c in self.companies]
        unique_names = set(names)
        
        if len(names) != len(unique_names):
            duplicates = [name for name in names if names.count(name) > 1]
            print(f"  ❌ 发现重复公司: {set(duplicates)}")
            score = 0
        else:
            print(f"  ✅ 无重复公司 ({len(names)} 家唯一公司)")
        
        self.validation_results['checks'].append({
            'name': '去重',
            'score': score,
            'max': 2,
            'passed': score == 2
        })
        
        print(f"\n得分: {score}/2\n")
        return score == 2
    
    def check_metadata(self) -> bool:
        """检查5：元数据"""
        print("检查5：元数据质量")
        print("-" * 60)
        
        score = 1
        
        for i, company in enumerate(self.companies):
            company_name = company.get('company_name', 'Unknown')
            source = company.get('source', '')
            
            if not source:
                print(f"  ⚠️  公司 {i+1} ({company_name[:30]}...): 缺少来源信息")
                score -= 0.1
            else:
                print(f"  ✅ 公司 {i+1} ({company_name[:30]}...): 来源={source}")
        
        score = max(0, score)
        
        self.validation_results['checks'].append({
            'name': '元数据',
            'score': score,
            'max': 1,
            'passed': score >= 0.7
        })
        
        print(f"\n得分: {score:.1f}/1\n")
        return score >= 0.7
    
    def auto_fix_issues(self):
        """自动修复问题"""
        print("=" * 60)
        print("自动修复问题")
        print("=" * 60)
        
        fixed_count = 0
        
        for company in self.companies:
            # 修复缺失的source
            if not company.get('source'):
                company['source'] = 'Public Information'
                fixed_count += 1
                print(f"  ✅ 为 '{company.get('company_name', 'Unknown')}' 添加source")
        
        if fixed_count > 0:
            # 保存修复后的数据
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({'companies': self.companies}, f, ensure_ascii=False, indent=2)
            print(f"\n✅ 修复了 {fixed_count} 个问题并保存")
        else:
            print("\n✅ 无需修复")
        
        print()
    
    def generate_report(self):
        """生成验证报告"""
        print("=" * 60)
        print("验证报告")
        print("=" * 60)
        
        total_score = sum(check['score'] for check in self.validation_results['checks'])
        max_score = sum(check['max'] for check in self.validation_results['checks'])
        
        print(f"\n总分: {total_score:.1f}/{max_score} ({total_score/max_score*100:.1f}%)\n")
        
        print("各项检查:")
        for check in self.validation_results['checks']:
            status = "✅ PASS" if check['passed'] else "❌ FAIL"
            print(f"  {status} | {check['name']}: {check['score']:.1f}/{check['max']}")
        
        print("\n数据统计:")
        print(f"  - 公司总数: {len(self.companies)}")
        
        from collections import Counter
        industries = Counter(c.get('industry', 'Unknown').split('/')[0] for c in self.companies)
        sizes = Counter(c.get('size', 'Unknown') for c in self.companies)
        
        print(f"  - 行业分布: {dict(industries.most_common(5))}")
        print(f"  - 规模分布: {dict(list(sizes.most_common(3)))}")
        
        avg_description = sum(len(c.get('description', '')) for c in self.companies) / len(self.companies)
        
        print(f"  - 平均描述长度: {avg_description:.0f} 字符")
        
        print("\n" + "=" * 60)
        
        if total_score >= 8:
            print("✅ 数据质量优秀！可以进行RAG导入测试")
            return True
        elif total_score >= 6:
            print("⚠️  数据质量一般，建议改进后再导入")
            return True
        else:
            print("❌ 数据质量不达标，需要修复")
            return False


def main():
    """主函数"""
    print("=" * 60)
    print("🏢 公司信息数据验证")
    print("=" * 60)
    print()
    
    # 文件路径
    file_path = Path(__file__).parent.parent / 'backend' / 'data' / 'crawled' / 'company_test.json'
    
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        sys.exit(1)
    
    # 创建验证器
    validator = CompanyDataValidator(str(file_path))
    
    # 加载数据
    validator.load_data()
    
    # 执行检查
    validator.check_completeness()
    validator.check_content_quality()
    validator.check_category_accuracy()
    validator.check_duplicates()
    validator.check_metadata()
    
    # 自动修复
    validator.auto_fix_issues()
    
    # 生成报告
    passed = validator.generate_report()
    
    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()







