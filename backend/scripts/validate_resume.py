"""
简历模板数据验证脚本
验证爬取的简历模板数据质量
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class ResumeValidator:
    """简历模板数据验证器"""
    
    def __init__(self):
        self.required_fields = ['template_name', 'industry', 'level', 'content', 'tips', 'source']
        self.issues = []
        self.warnings = []
        
    def load_data(self, file_path: str) -> Tuple[bool, Dict]:
        """加载简历模板数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'templates' in data:
                templates = data['templates']
                metadata = data.get('metadata', {})
            elif isinstance(data, list):
                templates = data
                metadata = {}
            else:
                self.issues.append("❌ 数据格式错误")
                return False, {}
            
            print(f"✅ 成功加载 {len(templates)} 个模板")
            return True, {'templates': templates, 'metadata': metadata}
            
        except Exception as e:
            self.issues.append(f"❌ 加载失败: {e}")
            return False, {}
    
    def validate_completeness(self, templates: List[Dict]) -> bool:
        """验证完整性"""
        print("\n1️⃣ 验证模板完整性...")
        all_valid = True
        
        for i, template in enumerate(templates):
            # 检查必填字段
            missing = [f for f in self.required_fields if f not in template]
            if missing:
                self.issues.append(f"❌ 模板 {i+1} 缺少字段: {', '.join(missing)}")
                all_valid = False
                continue
            
            # 检查字段是否为空
            if not template.get('template_name') or len(template['template_name'].strip()) == 0:
                self.issues.append(f"❌ 模板 {i+1} 名称为空")
                all_valid = False
            
            if not template.get('content') or len(template['content'].strip()) < 500:
                self.warnings.append(f"⚠️  模板 {i+1} 内容过短: {len(template.get('content', ''))} 字符")
            
            if not template.get('tips') or len(template['tips'].strip()) < 50:
                self.warnings.append(f"⚠️  模板 {i+1} 使用建议过短")
        
        if all_valid and not self.warnings:
            print(f"  ✅ 所有模板包含必填字段且内容完整")
        elif all_valid:
            print(f"  ⚡ 必填字段完整，但有 {len(self.warnings)} 个警告")
        
        return all_valid
    
    def validate_industry_level(self, templates: List[Dict]) -> bool:
        """验证行业和级别分类"""
        print("\n2️⃣ 验证行业和级别分类...")
        
        valid_levels = ['Entry Level', 'Junior Level', 'Mid Level', 'Mid-Senior Level', 'Senior Level', 'Executive Level']
        
        invalid_count = 0
        
        from collections import Counter
        industries = Counter()
        levels = Counter()
        
        for i, template in enumerate(templates):
            industry = template.get('industry', '')
            level = template.get('level', '')
            
            industries[industry] += 1
            levels[level] += 1
            
            # 检查level是否在标准列表中
            if level and level not in valid_levels:
                self.warnings.append(f"⚠️  模板 {i+1} 级别非标准: {level}")
        
        print(f"\n  行业分布:")
        for industry, count in industries.most_common():
            print(f"    {industry}: {count} 个")
        
        print(f"\n  级别分布:")
        for level, count in levels.most_common():
            print(f"    {level}: {count} 个")
        
        if invalid_count == 0:
            print(f"\n  ✅ 所有分类标准")
        else:
            print(f"\n  ⚠️  {invalid_count} 个分类需要调整")
        
        return invalid_count == 0
    
    def validate_content_quality(self, templates: List[Dict]) -> bool:
        """验证内容质量"""
        print("\n3️⃣ 验证内容质量...")
        
        quality_issues = 0
        
        for i, template in enumerate(templates):
            content = template.get('content', '')
            tips = template.get('tips', '')
            
            # 检查内容长度
            if len(content) < 1000:
                self.warnings.append(f"⚠️  模板 {i+1} 内容可能过简单（{len(content)} 字符）")
                quality_issues += 1
            
            # 检查是否包含关键元素
            required_sections = ['EXPERIENCE', 'EDUCATION', 'SKILLS', '经验', '教育', '技能']
            has_section = any(section.lower() in content.lower() for section in required_sections)
            
            if not has_section:
                self.warnings.append(f"⚠️  模板 {i+1} 可能缺少关键部分")
                quality_issues += 1
        
        if quality_issues == 0:
            print(f"  ✅ 所有模板内容质量良好")
        else:
            print(f"  ⚠️  {quality_issues} 个模板需要改进")
        
        return quality_issues == 0
    
    def check_duplicates(self, templates: List[Dict]) -> bool:
        """检查重复模板"""
        print("\n4️⃣ 检查重复模板...")
        
        names = [t.get('template_name', '') for t in templates]
        unique_names = set(names)
        
        duplicates = len(names) - len(unique_names)
        
        if duplicates == 0:
            print(f"  ✅ 无重复模板")
            return True
        else:
            print(f"  ❌ 发现 {duplicates} 个重复模板")
            self.issues.append(f"❌ 有 {duplicates} 个重复模板名称")
            return False
    
    def calculate_quality_score(self, templates: List[Dict]) -> float:
        """计算质量评分"""
        total_score = 10.0
        
        # 根据问题扣分
        total_score -= len(self.issues) * 1.0
        total_score -= len(self.warnings) * 0.2
        
        return max(0.0, min(10.0, total_score))
    
    def generate_report(self, score: float, templates: List[Dict]):
        """生成验证报告"""
        print("\n" + "=" * 80)
        print("📊 简历模板数据质量报告")
        print("=" * 80)
        
        print(f"\n数据统计:")
        print(f"  - 模板总数: {len(templates)}")
        
        # 行业统计
        from collections import Counter
        industries = Counter(t.get('industry', 'Unknown') for t in templates)
        print(f"  - 行业分布:")
        for industry, count in industries.items():
            print(f"    {industry}: {count} 个")
        
        # 级别统计
        levels = Counter(t.get('level', 'Unknown') for t in templates)
        print(f"  - 级别分布:")
        for level, count in levels.items():
            print(f"    {level}: {count} 个")
        
        # 内容统计
        avg_content_length = sum(len(t.get('content', '')) for t in templates) / len(templates)
        print(f"  - 平均内容长度: {avg_content_length:.0f} 字符")
        
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
            print("  ❌ 不合格 - 需要重新生成")
            status = "FAIL"
        
        print("=" * 80)
        
        return status


def main():
    """主函数"""
    print("=" * 80)
    print("🔍 简历模板数据验证")
    print("=" * 80)
    
    # 文件路径
    file_path = Path(__file__).parent.parent / 'backend' / 'data' / 'crawled' / 'resume_test.json'
    
    print(f"\n验证文件: {file_path}")
    
    # 创建验证器
    validator = ResumeValidator()
    
    # 1. 加载数据
    success, data = validator.load_data(str(file_path))
    if not success:
        print("\n❌ 验证失败")
        sys.exit(1)
    
    templates = data['templates']
    
    # 2. 验证完整性
    validator.validate_completeness(templates)
    
    # 3. 验证分类
    validator.validate_industry_level(templates)
    
    # 4. 验证内容质量
    validator.validate_content_quality(templates)
    
    # 5. 检查重复
    validator.check_duplicates(templates)
    
    # 6. 计算质量评分
    score = validator.calculate_quality_score(templates)
    
    # 7. 生成报告
    status = validator.generate_report(score, templates)
    
    # 8. 返回结果
    if status == "PASS" or status == "PASS_WITH_WARNINGS":
        print("\n✅ 验收通过！简历模板数据质量良好")
        sys.exit(0)
    else:
        print("\n❌ 验收失败！")
        sys.exit(1)


if __name__ == '__main__':
    main()

