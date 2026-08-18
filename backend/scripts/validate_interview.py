"""
面试题数据验证脚本
验证面试题的完整性、准确性和去重
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter


class InterviewValidator:
    """面试题数据验证器"""
    
    def __init__(self):
        self.required_fields = ['question', 'category', 'difficulty', 'answer', 'source']
        self.valid_categories = ['算法', '系统设计', '行为', 'database', 'network', 'security']
        self.valid_difficulties = ['简单', '中等', '困难', 'easy', 'medium', 'hard']
        self.issues = []
        self.warnings = []
        
    def load_data(self, file_path: str) -> Tuple[bool, Dict]:
        """加载面试题数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'questions' in data:
                questions = data['questions']
                metadata = data.get('metadata', {})
            elif isinstance(data, list):
                questions = data
                metadata = {}
            else:
                self.issues.append("❌ 数据格式错误：应该包含'questions'字段或为数组")
                return False, {}
            
            print(f"✅ 成功加载 {len(questions)} 道面试题")
            if metadata:
                print(f"ℹ️  元数据: {metadata.get('source', 'Unknown')}")
            
            return True, {'questions': questions, 'metadata': metadata}
            
        except FileNotFoundError:
            self.issues.append(f"❌ 文件不存在: {file_path}")
            return False, {}
        except json.JSONDecodeError as e:
            self.issues.append(f"❌ JSON解析失败: {e}")
            return False, {}
        except Exception as e:
            self.issues.append(f"❌ 加载失败: {e}")
            return False, {}
    
    def validate_completeness(self, questions: List[Dict]) -> bool:
        """验证问题完整性"""
        print("\n1️⃣ 验证问题完整性...")
        all_valid = True
        
        for i, q in enumerate(questions):
            missing_fields = [field for field in self.required_fields if field not in q]
            
            if missing_fields:
                self.issues.append(f"❌ 问题 {i+1} 缺少字段: {', '.join(missing_fields)}")
                all_valid = False
            else:
                # 检查字段是否为空
                empty_fields = [field for field in self.required_fields 
                               if not q.get(field) or str(q.get(field)).strip() == '']
                if empty_fields:
                    self.issues.append(f"❌ 问题 {i+1} 字段为空: {', '.join(empty_fields)}")
                    all_valid = False
                
                # 检查问题长度
                if len(q.get('question', '')) < 10:
                    self.warnings.append(f"⚠️  问题 {i+1} 内容过短: {len(q.get('question', ''))} 字符")
                
                # 检查答案长度
                if len(q.get('answer', '')) < 20:
                    self.warnings.append(f"⚠️  问题 {i+1} 答案过短: {len(q.get('answer', ''))} 字符")
        
        if all_valid:
            print(f"  ✅ 所有问题包含必填字段")
        
        return all_valid
    
    def validate_categories(self, questions: List[Dict]) -> bool:
        """验证分类准确性"""
        print("\n2️⃣ 验证分类准确性...")
        all_valid = True
        
        # 统计分类
        categories = [q.get('category', '') for q in questions]
        category_counts = Counter(categories)
        
        print(f"  分类分布:")
        for cat, count in category_counts.items():
            if cat not in self.valid_categories:
                self.warnings.append(f"⚠️  发现非标准分类: '{cat}'")
            print(f"    {cat}: {count} 道")
        
        # 验证难度
        difficulties = [q.get('difficulty', '') for q in questions]
        difficulty_counts = Counter(difficulties)
        
        print(f"  难度分布:")
        for diff, count in difficulty_counts.items():
            if diff not in self.valid_difficulties:
                self.warnings.append(f"⚠️  发现非标准难度: '{diff}'")
            print(f"    {diff}: {count} 道")
        
        return all_valid
    
    def check_duplicates(self, questions: List[Dict]) -> bool:
        """检查重复问题"""
        print("\n3️⃣ 检查重复问题...")
        
        # 使用问题文本的前100个字符作为唯一标识
        question_texts = {}
        duplicates = []
        
        for i, q in enumerate(questions):
            question_text = q.get('question', '')[:100].strip().lower()
            
            if question_text in question_texts:
                duplicates.append((i+1, question_texts[question_text]))
                self.warnings.append(f"⚠️  问题 {i+1} 可能与问题 {question_texts[question_text]} 重复")
            else:
                question_texts[question_text] = i+1
        
        if not duplicates:
            print(f"  ✅ 没有发现重复问题")
            return True
        else:
            print(f"  ⚠️  发现 {len(duplicates)} 个可能重复的问题")
            return False
    
    def calculate_quality_score(self, questions: List[Dict]) -> float:
        """计算数据质量评分"""
        total_score = 10.0
        
        # 检查项权重
        checks = {
            'completeness': 4.0,     # 完整性
            'categories': 2.0,       # 分类准确性
            'duplicates': 2.0,       # 无重复
            'content_quality': 2.0,  # 内容质量
        }
        
        # 根据问题扣分
        if self.issues:
            for issue in self.issues:
                if '缺少字段' in issue or '字段为空' in issue:
                    total_score -= checks['completeness'] / len(questions)
        
        # 根据警告扣分（少量）
        total_score -= len(self.warnings) * 0.2
        
        return max(0.0, min(10.0, total_score))
    
    def auto_fix(self, questions: List[Dict]) -> List[Dict]:
        """自动修复数据问题"""
        print("\n4️⃣ 自动修复问题...")
        fixed_count = 0
        
        for q in questions:
            # 标准化分类名称
            category = q.get('category', '')
            if category.lower() == 'algorithm':
                q['category'] = '算法'
                fixed_count += 1
            elif category.lower() == 'system design':
                q['category'] = '系统设计'
                fixed_count += 1
            elif category.lower() == 'behavioral':
                q['category'] = '行为'
                fixed_count += 1
            
            # 标准化难度
            difficulty = q.get('difficulty', '')
            if difficulty.lower() == 'easy':
                q['difficulty'] = '简单'
                fixed_count += 1
            elif difficulty.lower() == 'medium':
                q['difficulty'] = '中等'
                fixed_count += 1
            elif difficulty.lower() == 'hard':
                q['difficulty'] = '困难'
                fixed_count += 1
            
            # 确保有tags字段
            if 'tags' not in q:
                q['tags'] = [q.get('category', '未分类')]
                fixed_count += 1
        
        if fixed_count > 0:
            print(f"  🔧 自动修复了 {fixed_count} 个问题")
        else:
            print(f"  ℹ️  没有需要修复的问题")
        
        return questions
    
    def save_fixed_data(self, data: Dict, file_path: str):
        """保存修复后的数据"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\n✅ 修复后的数据已保存")
        except Exception as e:
            print(f"\n❌ 保存失败: {e}")
    
    def generate_report(self, score: float, questions: List[Dict]):
        """生成验证报告"""
        print("\n" + "=" * 80)
        print("📊 面试题数据质量报告")
        print("=" * 80)
        
        print(f"\n数据统计:")
        print(f"  - 总题数: {len(questions)}")
        
        categories = Counter(q.get('category', '') for q in questions)
        print(f"  - 分类统计:")
        for cat, count in categories.items():
            print(f"    {cat}: {count} 道 ({count/len(questions)*100:.1f}%)")
        
        difficulties = Counter(q.get('difficulty', '') for q in questions)
        print(f"  - 难度统计:")
        for diff, count in difficulties.items():
            print(f"    {diff}: {count} 道 ({count/len(questions)*100:.1f}%)")
        
        print(f"\n验证结果:")
        if not self.issues:
            print("  ✅ 没有发现严重问题")
        else:
            print(f"  ❌ 发现 {len(self.issues)} 个问题:")
            for issue in self.issues[:5]:  # 只显示前5个
                print(f"    {issue}")
        
        if self.warnings:
            print(f"\n  ⚠️  {len(self.warnings)} 个警告:")
            for warning in self.warnings[:5]:  # 只显示前5个
                print(f"    {warning}")
        
        print(f"\n数据质量评分: {score:.1f}/10.0")
        
        if score >= 8.0:
            print("  ✅ 优秀 - 可以直接使用")
            status = "PASS"
        elif score >= 6.0:
            print("  ⚡ 良好 - 建议修复后使用")
            status = "PASS_WITH_WARNINGS"
        else:
            print("  ❌ 不合格 - 需要重新生成或修复")
            status = "FAIL"
        
        print("=" * 80)
        
        return status


def main():
    """主函数"""
    print("=" * 80)
    print("🔍 面试题数据验证")
    print("=" * 80)
    
    # 文件路径
    file_path = Path(__file__).parent.parent / 'backend' / 'data' / 'crawled' / 'interview_test.json'
    
    print(f"\n验证文件: {file_path}")
    
    # 创建验证器
    validator = InterviewValidator()
    
    # 1. 加载数据
    success, data = validator.load_data(str(file_path))
    if not success:
        print("\n❌ 验证失败，请检查数据文件")
        sys.exit(1)
    
    questions = data['questions']
    
    # 2. 验证完整性
    validator.validate_completeness(questions)
    
    # 3. 验证分类
    validator.validate_categories(questions)
    
    # 4. 检查重复
    validator.check_duplicates(questions)
    
    # 5. 自动修复
    fixed_questions = validator.auto_fix(questions)
    
    # 6. 计算质量评分
    score = validator.calculate_quality_score(fixed_questions)
    
    # 7. 保存修复后的数据
    data['questions'] = fixed_questions
    validator.save_fixed_data(data, str(file_path))
    
    # 8. 生成报告
    status = validator.generate_report(score, fixed_questions)
    
    # 9. 返回结果
    if status == "PASS" or status == "PASS_WITH_WARNINGS":
        print("\n✅ 验收通过！面试题数据质量良好")
        sys.exit(0)
    else:
        print("\n❌ 验收失败！需要修复")
        sys.exit(1)


if __name__ == '__main__':
    main()

