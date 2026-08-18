"""
数据质量验证脚本
验证爬取数据的完整性和质量
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class DataValidator:
    """数据质量验证器"""
    
    def __init__(self):
        self.required_fields = ['title', 'content', 'source_url', 'category']
        self.optional_fields = ['subcategory', 'scraped_at', 'content_length', 'word_count']
        self.issues = []
        self.warnings = []
        
    def validate_json_format(self, file_path: str) -> Tuple[bool, List[Dict]]:
        """验证JSON格式"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                self.issues.append("❌ JSON应该是数组格式")
                return False, []
            
            print(f"✅ JSON格式正确（数组，包含{len(data)}条记录）")
            return True, data
            
        except json.JSONDecodeError as e:
            self.issues.append(f"❌ JSON解析失败: {e}")
            return False, []
        except FileNotFoundError:
            self.issues.append(f"❌ 文件不存在: {file_path}")
            return False, []
        except Exception as e:
            self.issues.append(f"❌ 读取文件失败: {e}")
            return False, []
    
    def validate_required_fields(self, data: List[Dict]) -> bool:
        """验证必填字段"""
        all_valid = True
        
        for i, item in enumerate(data):
            missing_fields = [field for field in self.required_fields if field not in item]
            
            if missing_fields:
                self.issues.append(f"❌ 记录 {i+1} 缺少字段: {', '.join(missing_fields)}")
                all_valid = False
            else:
                # 检查字段是否为空
                empty_fields = [field for field in self.required_fields 
                               if not item.get(field) or str(item.get(field)).strip() == '']
                if empty_fields:
                    self.issues.append(f"❌ 记录 {i+1} 字段为空: {', '.join(empty_fields)}")
                    all_valid = False
        
        if all_valid:
            print(f"✅ 所有必填字段完整 ({', '.join(self.required_fields)})")
        
        return all_valid
    
    def validate_content_length(self, data: List[Dict]) -> bool:
        """验证内容长度"""
        all_valid = True
        
        for i, item in enumerate(data):
            content = item.get('content', '')
            content_len = len(content)
            
            if content_len < 100:
                self.issues.append(f"❌ 记录 {i+1} 内容过短: {content_len} 字符 (要求>100)")
                all_valid = False
            elif content_len < 500:
                self.warnings.append(f"⚠️  记录 {i+1} 内容较短: {content_len} 字符")
            else:
                print(f"✅ 记录 {i+1} 内容长度合理: {content_len} 字符")
        
        return all_valid
    
    def validate_url_format(self, data: List[Dict]) -> bool:
        """验证URL格式"""
        import re
        url_pattern = re.compile(r'^https?://')
        
        all_valid = True
        for i, item in enumerate(data):
            url = item.get('source_url', '')
            if not url_pattern.match(url):
                self.issues.append(f"❌ 记录 {i+1} URL格式无效: {url}")
                all_valid = False
        
        if all_valid:
            print(f"✅ 所有URL格式正确")
        
        return all_valid
    
    def calculate_quality_score(self, data: List[Dict]) -> float:
        """计算数据质量评分 (0-10分)"""
        total_score = 10.0
        
        # 检查项权重
        checks = {
            'json_format': 2.0,      # JSON格式正确
            'required_fields': 3.0,  # 必填字段完整
            'content_length': 2.5,   # 内容长度合理
            'url_format': 1.0,       # URL格式正确
            'metadata': 1.5,         # 元数据完整
        }
        
        # 根据问题扣分
        if self.issues:
            for issue in self.issues:
                if 'JSON' in issue:
                    total_score -= checks['json_format']
                elif '缺少字段' in issue or '字段为空' in issue:
                    total_score -= checks['required_fields'] / len(data)
                elif '内容过短' in issue:
                    total_score -= checks['content_length'] / len(data)
                elif 'URL' in issue:
                    total_score -= checks['url_format'] / len(data)
        
        # 根据警告扣分（少量）
        total_score -= len(self.warnings) * 0.1
        
        return max(0.0, min(10.0, total_score))
    
    def auto_fix_data(self, data: List[Dict], file_path: str) -> List[Dict]:
        """自动修复数据问题"""
        fixed_data = []
        fixed_count = 0
        
        for item in data:
            fixed_item = item.copy()
            
            # 修复：移除多余空白
            if 'content' in fixed_item:
                original_content = fixed_item['content']
                cleaned_content = ' '.join(original_content.split())
                if cleaned_content != original_content:
                    fixed_item['content'] = cleaned_content
                    fixed_count += 1
            
            # 修复：添加默认category
            if not fixed_item.get('category'):
                fixed_item['category'] = 'academic'
                fixed_count += 1
            
            # 修复：确保content_length准确
            if 'content' in fixed_item:
                actual_length = len(fixed_item['content'])
                if fixed_item.get('content_length') != actual_length:
                    fixed_item['content_length'] = actual_length
                    fixed_count += 1
            
            fixed_data.append(fixed_item)
        
        if fixed_count > 0:
            # 保存修复后的数据
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(fixed_data, f, ensure_ascii=False, indent=2)
            print(f"\n🔧 自动修复了 {fixed_count} 个小问题")
        
        return fixed_data
    
    def generate_report(self, score: float, data: List[Dict]):
        """生成验证报告"""
        print("\n" + "=" * 80)
        print("📊 数据质量报告")
        print("=" * 80)
        
        print(f"\n数据统计:")
        print(f"  - 记录数量: {len(data)}")
        if data:
            print(f"  - 平均内容长度: {sum(item.get('content_length', 0) for item in data) / len(data):.0f} 字符")
            print(f"  - 平均词数: {sum(item.get('word_count', 0) for item in data) / len(data):.0f} 词")
        
        print(f"\n验证结果:")
        if not self.issues:
            print("  ✅ 没有发现严重问题")
        else:
            print(f"  ❌ 发现 {len(self.issues)} 个问题:")
            for issue in self.issues:
                print(f"    {issue}")
        
        if self.warnings:
            print(f"\n  ⚠️  {len(self.warnings)} 个警告:")
            for warning in self.warnings:
                print(f"    {warning}")
        
        print(f"\n数据质量评分: {score:.1f}/10.0")
        
        if score >= 8.0:
            print("  ✅ 优秀 - 可以直接使用")
            status = "PASS"
        elif score >= 6.0:
            print("  ⚡ 良好 - 建议修复后使用")
            status = "PASS_WITH_WARNINGS"
        else:
            print("  ❌ 不合格 - 需要重新爬取或修复")
            status = "FAIL"
        
        print("=" * 80)
        
        return status


def main():
    """主函数"""
    print("=" * 80)
    print("🔍 数据质量验证")
    print("=" * 80)
    
    # 文件路径（正确的路径）
    file_path = Path(__file__).parent.parent / 'backend' / 'data' / 'crawled' / 'academic_test.json'
    
    if not file_path.exists():
        # 尝试另一个路径
        file_path = Path(__file__).parent.parent / 'data' / 'crawled' / 'academic_test.json'
    
    print(f"\n验证文件: {file_path}")
    print(f"文件存在: {file_path.exists()}")
    
    # 创建验证器
    validator = DataValidator()
    
    # 1. 验证JSON格式
    print("\n1️⃣ 验证JSON格式...")
    is_valid, data = validator.validate_json_format(str(file_path))
    
    if not is_valid:
        print("\n❌ 验证失败，请检查JSON文件")
        sys.exit(1)
    
    # 2. 验证必填字段
    print("\n2️⃣ 验证必填字段...")
    validator.validate_required_fields(data)
    
    # 3. 验证内容长度
    print("\n3️⃣ 验证内容长度...")
    validator.validate_content_length(data)
    
    # 4. 验证URL格式
    print("\n4️⃣ 验证URL格式...")
    validator.validate_url_format(data)
    
    # 5. 自动修复
    print("\n5️⃣ 自动修复...")
    fixed_data = validator.auto_fix_data(data, str(file_path))
    
    # 6. 计算质量评分
    score = validator.calculate_quality_score(fixed_data)
    
    # 7. 生成报告
    status = validator.generate_report(score, fixed_data)
    
    # 8. 返回结果
    if status == "PASS":
        print("\n✅ 验收通过！数据质量>8/10")
        sys.exit(0)
    elif status == "PASS_WITH_WARNINGS":
        print("\n⚡ 验收通过（有警告）")
        sys.exit(0)
    else:
        print("\n❌ 验收失败！需要修复")
        sys.exit(1)


if __name__ == '__main__':
    main()

