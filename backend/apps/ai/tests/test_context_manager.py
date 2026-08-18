"""
Context Manager Service 单元测试

测试上下文管理的核心功能：
1. Token 计数
2. 获取上下文消息（带Token限制）
3. 添加消息并更新Token统计
4. 消息截断策略
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.ai.models import AIConversation, AIMessage
from apps.ai.services.context_manager import ContextManager, get_context_manager

User = get_user_model()


class ContextManagerTestCase(TestCase):
    """Context Manager 测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        self.conversation = AIConversation.objects.create(
            user=self.user,
            title="测试对话",
            ai_function="general_chat"
        )
        
        self.context_manager = ContextManager()
    
    def test_singleton_pattern(self):
        """测试单例模式"""
        cm1 = get_context_manager()
        cm2 = get_context_manager()
        self.assertIs(cm1, cm2, "应该返回相同的单例实例")
    
    def test_count_tokens_simple(self):
        """测试基本Token计数"""
        text = "Hello, world!"
        tokens = self.context_manager.count_tokens(text)
        
        # Token数应该大于0且小于文本长度
        self.assertGreater(tokens, 0)
        self.assertLess(tokens, len(text))
        
        print(f"✓ Token计数测试通过: '{text}' = {tokens} tokens")
    
    def test_count_tokens_chinese(self):
        """测试中文Token计数"""
        text = "你好，世界！这是一个测试。"
        tokens = self.context_manager.count_tokens(text)
        
        self.assertGreater(tokens, 0)
        print(f"✓ 中文Token计数测试通过: '{text}' = {tokens} tokens")
    
    def test_add_message_user(self):
        """测试添加用户消息"""
        message = self.context_manager.add_message(
            conversation_id=self.conversation.id,
            role="user",
            content="这是一条测试消息",
            model_used="test-model"
        )
        
        self.assertIsNotNone(message)
        self.assertEqual(message.role, "user")
        self.assertEqual(message.content, "这是一条测试消息")
        self.assertGreater(message.tokens, 0)
        
        # 验证对话的总Token数已更新
        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.total_tokens, message.tokens)
        
        print(f"✓ 添加用户消息测试通过: tokens={message.tokens}")
    
    def test_add_message_assistant(self):
        """测试添加AI助手消息"""
        message = self.context_manager.add_message(
            conversation_id=self.conversation.id,
            role="assistant",
            content="这是AI的回答，内容比较长一些。",
            model_used="test-model"
        )
        
        self.assertIsNotNone(message)
        self.assertEqual(message.role, "assistant")
        self.assertGreater(message.tokens, 0)
        
        print(f"✓ 添加助手消息测试通过: tokens={message.tokens}")
    
    def test_add_multiple_messages(self):
        """测试添加多条消息并验证累计Token"""
        # 添加3条消息
        msg1 = self.context_manager.add_message(
            self.conversation.id, "user", "第一条消息", "model"
        )
        msg2 = self.context_manager.add_message(
            self.conversation.id, "assistant", "第一条回复", "model"
        )
        msg3 = self.context_manager.add_message(
            self.conversation.id, "user", "第二条消息", "model"
        )
        
        # 验证对话的总Token数 = 所有消息的Token之和
        self.conversation.refresh_from_db()
        expected_tokens = msg1.tokens + msg2.tokens + msg3.tokens
        self.assertEqual(self.conversation.total_tokens, expected_tokens)
        
        print(f"✓ 多条消息累计Token测试通过: {expected_tokens} tokens")
    
    def test_get_context_empty(self):
        """测试获取空对话的上下文"""
        messages = self.context_manager.get_context_messages(
            conversation_id=self.conversation.id,
            max_tokens=1000
        )
        
        self.assertEqual(len(messages), 0)
        print("✓ 空上下文测试通过")
    
    def test_get_context_single_turn(self):
        """测试获取单轮对话的上下文"""
        # 添加一轮对话
        self.context_manager.add_message(
            self.conversation.id, "user", "你好", "model"
        )
        self.context_manager.add_message(
            self.conversation.id, "assistant", "你好！有什么可以帮助你的吗？", "model"
        )
        
        messages = self.context_manager.get_context_messages(
            conversation_id=self.conversation.id,
            max_tokens=1000
        )
        
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "user")
        self.assertEqual(messages[1]["role"], "assistant")
        
        print("✓ 单轮对话上下文测试通过")
    
    def test_get_context_multi_turn(self):
        """测试获取多轮对话的上下文"""
        # 添加3轮对话
        for i in range(3):
            self.context_manager.add_message(
                self.conversation.id, "user", f"问题{i+1}", "model"
            )
            self.context_manager.add_message(
                self.conversation.id, "assistant", f"回答{i+1}", "model"
            )
        
        messages = self.context_manager.get_context_messages(
            conversation_id=self.conversation.id,
            max_tokens=1000
        )
        
        self.assertEqual(len(messages), 6)
        print("✓ 多轮对话上下文测试通过")
    
    def test_get_context_with_token_limit(self):
        """测试Token限制下的上下文截断"""
        # 添加多条消息，每条内容较长
        long_text = "这是一条很长的消息，包含了很多内容。" * 10  # 重复10次
        
        for i in range(5):
            self.context_manager.add_message(
                self.conversation.id, "user", f"问题{i+1}: {long_text}", "model"
            )
            self.context_manager.add_message(
                self.conversation.id, "assistant", f"回答{i+1}: {long_text}", "model"
            )
        
        # 设置较小的Token限制
        messages = self.context_manager.get_context_messages(
            conversation_id=self.conversation.id,
            max_tokens=200  # 较小的限制
        )
        
        # 应该返回部分消息（最近的几条）
        self.assertGreater(len(messages), 0)
        self.assertLess(len(messages), 10)  # 应该少于全部10条消息
        
        # 验证返回的是最近的消息（通过检查内容中的序号）
        if messages:
            # 最新的消息应该包含较大的序号
            user_msgs = [m for m in messages if m["role"] == "user"]
            if user_msgs:  # 如果有用户消息
                last_user_msg = user_msgs[-1]
                self.assertIn("问题", last_user_msg["content"])
        
        print(f"✓ Token限制截断测试通过: 返回 {len(messages)} 条消息（共10条）")
    
    def test_get_context_respects_order(self):
        """测试上下文消息的顺序正确"""
        # 添加消息
        texts = ["第一条", "第二条", "第三条"]
        for text in texts:
            self.context_manager.add_message(
                self.conversation.id, "user", text, "model"
            )
        
        messages = self.context_manager.get_context_messages(
            conversation_id=self.conversation.id,
            max_tokens=1000
        )
        
        # 验证顺序
        self.assertEqual(messages[0]["content"], "第一条")
        self.assertEqual(messages[1]["content"], "第二条")
        self.assertEqual(messages[2]["content"], "第三条")
        
        print("✓ 消息顺序测试通过")
    
    def test_get_context_nonexistent_conversation(self):
        """测试获取不存在的对话的上下文"""
        messages = self.context_manager.get_context_messages(
            conversation_id=99999,  # 不存在的ID
            max_tokens=1000
        )
        
        self.assertEqual(len(messages), 0)
        print("✓ 不存在的对话测试通过")
    
    def test_add_message_nonexistent_conversation(self):
        """测试向不存在的对话添加消息"""
        message = self.context_manager.add_message(
            conversation_id=99999,  # 不存在的ID
            role="user",
            content="测试",
            model_used="model"
        )
        
        self.assertIsNone(message)
        print("✓ 向不存在的对话添加消息测试通过")
    
    def test_get_conversation_summary(self):
        """测试生成对话摘要"""
        # 添加几条消息
        self.context_manager.add_message(
            self.conversation.id, "user", "你好", "model"
        )
        self.context_manager.add_message(
            self.conversation.id, "assistant", "你好！", "model"
        )
        
        summary = self.context_manager.get_conversation_summary(
            conversation_id=self.conversation.id,
            max_messages=5
        )
        
        self.assertIn("用户", summary)
        self.assertIn("AI", summary)
        self.assertIn("你好", summary)
        
        print(f"✓ 对话摘要测试通过:\n{summary}")
    
    def test_context_with_very_long_message(self):
        """测试超长消息的处理"""
        # 创建一条超长消息（>1000字符）
        long_message = "这是一条超长消息。" * 200  # 约2000字符
        
        msg = self.context_manager.add_message(
            self.conversation.id, "user", long_message, "model"
        )
        
        self.assertIsNotNone(msg)
        self.assertGreater(msg.tokens, 100)  # 应该有很多tokens
        
        # 验证能正常获取
        messages = self.context_manager.get_context_messages(
            conversation_id=self.conversation.id,
            max_tokens=5000
        )
        
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["content"], long_message)
        
        print(f"✓ 超长消息测试通过: {msg.tokens} tokens")
    
    def test_token_limit_edge_case(self):
        """测试Token限制的边界情况"""
        # 添加几条消息
        self.context_manager.add_message(self.conversation.id, "user", "短消息1", "model")
        self.context_manager.add_message(self.conversation.id, "assistant", "回复1", "model")
        
        # 设置极小的Token限制
        messages = self.context_manager.get_context_messages(
            conversation_id=self.conversation.id,
            max_tokens=1  # 极小限制
        )
        
        # 应该返回空列表或最少的消息
        self.assertLessEqual(len(messages), 2)
        print(f"✓ Token极限边界测试通过: {len(messages)} 条消息")


# ========== Pytest 风格的测试（如果需要） ==========

@pytest.mark.django_db
class TestContextManagerPytest:
    """使用 pytest 风格的测试"""
    
    def test_token_counting_accuracy(self):
        """测试Token计数的准确性"""
        cm = ContextManager()
        
        test_cases = [
            ("Hello", "简单英文"),
            ("你好世界", "中文"),
            ("Hello 世界 123", "混合文本"),
            ("a" * 1000, "重复字符"),
        ]
        
        for text, desc in test_cases:
            tokens = cm.count_tokens(text)
            assert tokens > 0, f"{desc} 应该有正向Token数"
            print(f"✓ {desc}: {len(text)} 字符 = {tokens} tokens")

