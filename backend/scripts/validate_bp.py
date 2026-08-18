"""
商业计划书模板数据验证脚本
验证BP模板的数据质量
"""

import json
from pathlib import Path
from typing import Dict, List
import sys


class BPDataValidator:
    """BP数据验证器"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.templates = []
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
        
        self.templates = data.get('templates', data if isinstance(data, list) else [])
        print(f"✅ 加载了 {len(self.templates)} 个BP模板\n")
    
    def check_completeness(self) -> bool:
        """检查1：数据完整性"""
        print("检查1：数据完整性")
        print("-" * 60)
        
        required_fields = ['template_name', 'industry', 'stage', 'content', 'tips', 'source']
        score = 2
        
        for i, template in enumerate(self.templates):
            missing = [field for field in required_fields if not template.get(field)]
            
            if missing:
                print(f"  ❌ 模板 {i+1}: 缺少字段 {missing}")
                score = 0
            else:
                print(f"  ✅ 模板 {i+1}: 所有字段完整")
        
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
        
        for i, template in enumerate(self.templates):
            template_name = template.get('template_name', 'Unknown')
            content = template.get('content', '')
            tips = template.get('tips', '')
            
            # 检查内容长度
            if len(content) < 3000:
                issues.append(f"模板 {i+1} ({template_name}): 内容过短 ({len(content)}字符)")
                score -= 0.5
            else:
                print(f"  ✅ 模板 {i+1} ({template_name[:30]}...): 内容充足 ({len(content)}字符)")
            
            # 检查tips
            if len(tips) < 200:
                issues.append(f"模板 {i+1} ({template_name}): Tips过短")
                score -= 0.5
            else:
                print(f"  ✅ 模板 {i+1} ({template_name[:30]}...): Tips详尽 ({len(tips)}字符)")
        
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
        
        print(f"\n得分: {score}/3\n")
        return score >= 2.5
    
    def check_category_accuracy(self) -> bool:
        """检查3：分类准确性"""
        print("检查3：分类准确性")
        print("-" * 60)
        
        score = 2
        
        valid_stages = ['Seed', 'Series A', 'Series B', 'Growth', 'Startup', 'Early Growth', 'Foundation']
        
        for i, template in enumerate(self.templates):
            template_name = template.get('template_name', 'Unknown')
            industry = template.get('industry', '')
            stage = template.get('stage', '')
            
            # 检查行业
            if not industry or industry == 'Unknown':
                print(f"  ⚠️  模板 {i+1}: 行业未指定")
                score -= 0.3
            else:
                print(f"  ✅ 模板 {i+1} ({template_name[:30]}...): 行业={industry}")
            
            # 检查阶段
            if not any(valid in stage for valid in valid_stages):
                print(f"  ⚠️  模板 {i+1}: 阶段标签不标准 ({stage})")
                score -= 0.3
            else:
                print(f"  ✅ 模板 {i+1} ({template_name[:30]}...): 阶段={stage}")
        
        score = max(0, score)
        
        self.validation_results['checks'].append({
            'name': '分类准确性',
            'score': score,
            'max': 2,
            'passed': score >= 1.5
        })
        
        print(f"\n得分: {score}/2\n")
        return score >= 1.5
    
    def check_duplicates(self) -> bool:
        """检查4：去重"""
        print("检查4：重复检测")
        print("-" * 60)
        
        score = 2
        
        names = [t.get('template_name', '') for t in self.templates]
        unique_names = set(names)
        
        if len(names) != len(unique_names):
            duplicates = [name for name in names if names.count(name) > 1]
            print(f"  ❌ 发现重复模板: {set(duplicates)}")
            score = 0
        else:
            print(f"  ✅ 无重复模板 ({len(names)} 个唯一模板)")
        
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
        
        for i, template in enumerate(self.templates):
            template_name = template.get('template_name', 'Unknown')
            tags = template.get('tags', [])
            source = template.get('source', '')
            
            if not tags or len(tags) < 2:
                print(f"  ⚠️  模板 {i+1} ({template_name[:30]}...): 标签不足")
                score -= 0.2
            else:
                print(f"  ✅ 模板 {i+1} ({template_name[:30]}...): {len(tags)} 个标签")
            
            if not source:
                print(f"  ⚠️  模板 {i+1}: 缺少来源信息")
                score -= 0.2
        
        score = max(0, score)
        
        self.validation_results['checks'].append({
            'name': '元数据',
            'score': score,
            'max': 1,
            'passed': score >= 0.7
        })
        
        print(f"\n得分: {score}/1\n")
        return score >= 0.7
    
    def auto_fix_issues(self):
        """自动修复问题"""
        print("=" * 60)
        print("自动修复问题")
        print("=" * 60)
        
        fixed_count = 0
        
        for template in self.templates:
            # 修复缺失的tags
            if not template.get('tags'):
                template['tags'] = ['business-plan', template.get('industry', 'general').lower().replace('/', '-')]
                fixed_count += 1
                print(f"  ✅ 为 '{template.get('template_name', 'Unknown')}' 添加默认tags")
            
            # 修复缺失的source
            if not template.get('source'):
                template['source'] = 'Generated Template'
                fixed_count += 1
                print(f"  ✅ 为 '{template.get('template_name', 'Unknown')}' 添加source")
        
        if fixed_count > 0:
            # 保存修复后的数据
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({'templates': self.templates}, f, ensure_ascii=False, indent=2)
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
        print(f"  - 模板总数: {len(self.templates)}")
        
        from collections import Counter
        industries = Counter(t.get('industry', 'Unknown') for t in self.templates)
        stages = Counter(t.get('stage', 'Unknown') for t in self.templates)
        
        print(f"  - 行业分布: {dict(industries)}")
        print(f"  - 阶段分布: {dict(stages)}")
        
        avg_content = sum(len(t.get('content', '')) for t in self.templates) / len(self.templates)
        avg_tips = sum(len(t.get('tips', '')) for t in self.templates) / len(self.templates)
        
        print(f"  - 平均内容长度: {avg_content:.0f} 字符")
        print(f"  - 平均Tips长度: {avg_tips:.0f} 字符")
        
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
    print("📄 商业计划书模板数据验证")
    print("=" * 60)
    print()
    
    # 文件路径（修正路径）
    file_path = Path(__file__).parent.parent / 'backend' / 'data' / 'crawled' / 'bp_test.json'
    
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        sys.exit(1)
    
    # 创建验证器
    validator = BPDataValidator(str(file_path))
    
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







