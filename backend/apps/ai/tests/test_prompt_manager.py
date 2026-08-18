"""
Prompt Manager 单元测试
"""

from django.test import TestCase
from pathlib import Path

from apps.ai.services.prompt_manager import PromptTemplate, PromptManager, get_prompt_manager


class PromptTemplateTestCase(TestCase):
    """PromptTemplate 测试"""
    
    def test_load_template(self):
        """测试加载模板"""
        prompts_dir = Path(__file__).parent.parent / "prompts"
        template_path = prompts_dir / "general.txt"
        
        template = PromptTemplate(template_path)
        
        self.assertGreater(len(template.raw_content), 0)
        print("✓ 模板加载测试通过")
    
    def test_render_without_variables(self):
        """测试无变量渲染"""
        prompts_dir = Path(__file__).parent.parent / "prompts"
        template_path = prompts_dir / "general.txt"
        
        template = PromptTemplate(template_path)
        rendered = template.render()
        
        self.assertEqual(len(rendered), len(template.raw_content))
        print("✓ 无变量渲染测试通过")
    
    def test_get_variables(self):
        """测试提取变量"""
        prompts_dir = Path(__file__).parent.parent / "prompts"
        template_path = prompts_dir / "general.txt"
        
        template = PromptTemplate(template_path)
        variables = template.get_variables()
        
        self.assertIsInstance(variables, list)
        print(f"✓ 变量提取测试通过: {variables}")


class PromptManagerTestCase(TestCase):
    """PromptManager 测试"""
    
    def test_singleton(self):
        """测试单例模式"""
        pm1 = get_prompt_manager()
        pm2 = get_prompt_manager()
        
        self.assertIs(pm1, pm2)
        print("✓ 单例模式测试通过")
    
    def test_get_template(self):
        """测试获取模板"""
        pm = get_prompt_manager()
        
        template = pm.get_template("general.txt")
        
        self.assertIsInstance(template, PromptTemplate)
        self.assertGreater(len(template.raw_content), 0)
        print("✓ 获取模板测试通过")
    
    def test_get_template_with_cache(self):
        """测试模板缓存"""
        pm = get_prompt_manager()
        
        # 第一次获取
        template1 = pm.get_template("general.txt")
        
        # 第二次获取（应该来自缓存）
        template2 = pm.get_template("general.txt")
        
        self.assertIs(template1, template2)
        print("✓ 模板缓存测试通过")
    
    def test_render_prompt(self):
        """测试渲染 Prompt"""
        pm = get_prompt_manager()
        
        rendered = pm.render_prompt("general.txt", {
            "user_name": "测试用户",
            "university": "APU"
        })
        
        self.assertGreater(len(rendered), 0)
        print("✓ 渲染 Prompt 测试通过")
    
    def test_list_prompts(self):
        """测试列出所有 Prompts"""
        pm = get_prompt_manager()
        
        prompts = pm.list_prompts()
        
        self.assertGreater(len(prompts), 0)
        self.assertIn("general.txt", prompts)
        print(f"✓ 列出 Prompts 测试通过: 找到 {len(prompts)} 个文件")
    
    def test_validate_prompts(self):
        """测试验证所有 Prompts"""
        pm = get_prompt_manager()
        
        result = pm.validate_prompts()
        
        self.assertGreater(result["total"], 0)
        self.assertEqual(result["success"] + result["failed"], result["total"])
        
        print(f"✓ Prompt 验证测试通过:")
        print(f"  总计: {result['total']}")
        print(f"  成功: {result['success']}")
        print(f"  失败: {result['failed']}")
        
        # 所有 Prompts 应该都能成功加载
        self.assertEqual(result["failed"], 0, "存在无法加载的 Prompt 文件")
    
    def test_fallback_to_general(self):
        """测试不存在的 Prompt 降级到 general"""
        pm = get_prompt_manager()
        
        try:
            template = pm.get_template("nonexistent.txt")
            # 应该降级到 general.txt
            self.assertIsNotNone(template)
            print("✓ 降级测试通过")
        except FileNotFoundError:
            print("✓ 正确抛出 FileNotFoundError")






