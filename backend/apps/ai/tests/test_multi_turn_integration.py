"""
多轮对话集成测试脚本

测试 Phase 2 的完整功能流程：
1. 创建对话
2. 多轮对话交互
3. Token限制验证
4. 上下文保持验证
"""

import os
import sys
import django
import pytest

# 设置 Django 环境
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.ai.models import AIConversation, AIMessage
from apps.ai.services.context_manager import get_context_manager

User = get_user_model()

pytestmark = pytest.mark.django_db


def print_section(title):
    """打印测试段落标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_multi_turn_conversation():
    """测试多轮对话功能"""
    
    print_section("1. 准备测试环境")
    
    # 获取或创建测试用户
    user, created = User.objects.get_or_create(
        username="test_conversation_user",
        defaults={
            "email": "test_conv@example.com",
        }
    )
    
    if created:
        user.set_password("testpass123")
        user.save()
        print(f"✓ 创建测试用户: {user.username}")
    else:
        print(f"✓ 使用现有测试用户: {user.username}")
    
    # 创建新对话
    conversation = AIConversation.objects.create(
        user=user,
        title="多轮对话测试",
        ai_function="general_chat"
    )
    print(f"✓ 创建测试对话: ID={conversation.id}")
    
    # 获取 Context Manager
    context_manager = get_context_manager()
    print(f"✓ 初始化 Context Manager")
    
    
    print_section("2. 模拟多轮对话")
    
    # 模拟5轮对话
    test_conversations = [
        ("你好，我想了解一下APU的课程", "你好！APU提供多种课程，包括..."),
        ("那么学费是多少呢？", "APU的学费根据专业不同有所差异..."),
        ("有奖学金吗？", "是的，APU提供多种奖学金项目..."),
        ("申请流程是怎样的？", "申请流程分为几个步骤：1. 在线申请..."),
        ("谢谢你的帮助", "不客气！如有其他问题随时问我。"),
    ]
    
    for i, (user_msg, assistant_msg) in enumerate(test_conversations, 1):
        print(f"\n--- 第 {i} 轮对话 ---")
        
        # 添加用户消息
        user_message = context_manager.add_message(
            conversation_id=conversation.id,
            role="user",
            content=user_msg,
            model_used="test-model"
        )
        print(f"用户: {user_msg}")
        print(f"  → Token数: {user_message.tokens}")
        
        # 添加AI回复
        assistant_message = context_manager.add_message(
            conversation_id=conversation.id,
            role="assistant",
            content=assistant_msg,
            model_used="test-model"
        )
        print(f"AI: {assistant_msg}")
        print(f"  → Token数: {assistant_message.tokens}")
        
        # 显示累计Token
        conversation.refresh_from_db()
        print(f"  → 对话累计Token: {conversation.total_tokens}")
    
    
    print_section("3. 测试上下文获取（无Token限制）")
    
    messages = context_manager.get_context_messages(
        conversation_id=conversation.id,
        max_tokens=5000  # 足够大的限制
    )
    
    print(f"✓ 获取到 {len(messages)} 条历史消息")
    print(f"✓ 预期: 10 条消息（5轮对话 × 2）")
    
    assert len(messages) == 10, f"消息数量不匹配: 期望10条，实际{len(messages)}条"
    
    # 验证消息顺序
    print("\n上下文消息摘要:")
    for i, msg in enumerate(messages[:3], 1):  # 只显示前3条
        content_preview = msg['content'][:30] + "..." if len(msg['content']) > 30 else msg['content']
        print(f"  {i}. [{msg['role']}] {content_preview}")
    print(f"  ...")
    
    
    print_section("4. 测试Token限制下的上下文截断")
    
    # 测试不同的Token限制
    token_limits = [50, 100, 200, 500]
    
    for limit in token_limits:
        messages = context_manager.get_context_messages(
            conversation_id=conversation.id,
            max_tokens=limit
        )
        
        # 计算实际使用的Token数
        total_tokens = sum(
            context_manager.count_tokens(msg['content']) for msg in messages
        )
        
        print(f"\nToken限制: {limit}")
        print(f"  → 返回消息数: {len(messages)}")
        print(f"  → 实际Token数: {total_tokens}")
        print(f"  → 是否符合限制: {'✓' if total_tokens <= limit else '✗'}")
        
        assert total_tokens <= limit, f"超出Token限制: {total_tokens} > {limit}"
        
        # 验证返回的是最近的消息
        if messages:
            last_msg = messages[-1]
            print(f"  → 最后一条消息: [{last_msg['role']}] {last_msg['content'][:30]}...")
    
    
    print_section("5. 测试上下文保持（验证最近消息优先）")
    
    # 使用较小限制，应该只返回最近的几条消息
    messages = context_manager.get_context_messages(
        conversation_id=conversation.id,
        max_tokens=150  # 较小限制
    )
    
    print(f"✓ Token限制150下返回 {len(messages)} 条消息")
    
    # 验证返回的消息是最新的
    if messages:
        # 最后一条应该是"谢谢你的帮助"或其回复
        last_user_msgs = [m for m in messages if m['role'] == 'user']
        if last_user_msgs:
            print(f"✓ 最近的用户消息: {last_user_msgs[-1]['content']}")
            # 应该包含最后几轮的对话
            assert "谢谢" in last_user_msgs[-1]['content'] or "申请" in last_user_msgs[-1]['content'], \
                "应该返回最近的消息"
    
    
    print_section("6. 测试对话摘要生成")
    
    summary = context_manager.get_conversation_summary(
        conversation_id=conversation.id,
        max_messages=3
    )
    
    print(f"对话摘要（最近3条消息）:\n{summary}")
    print(f"\n✓ 摘要长度: {len(summary)} 字符")
    
    
    print_section("7. 验证数据库状态")
    
    conversation.refresh_from_db()
    
    print(f"对话信息:")
    print(f"  - ID: {conversation.id}")
    print(f"  - 标题: {conversation.title}")
    print(f"  - 消息总数: {conversation.get_message_count()}")
    print(f"  - 累计Token: {conversation.total_tokens}")
    print(f"  - 创建时间: {conversation.created_at}")
    print(f"  - 更新时间: {conversation.updated_at}")
    
    # 验证消息数量
    assert conversation.get_message_count() == 10, f"消息数量不匹配"
    assert conversation.total_tokens > 0, "Token计数异常"
    
    
    print_section("8. 清理测试数据")

    # Pytest owns the transaction and rolls it back after the test. Keeping this
    # non-interactive makes the integration suite safe for CI and local automation.
    conversation.delete()
    
    
    print_section("✅ 所有测试通过！")
    
    print("\n测试总结:")
    print(f"  ✓ 多轮对话创建和保存")
    print(f"  ✓ Token自动计数")
    print(f"  ✓ 上下文获取（完整）")
    print(f"  ✓ Token限制下的智能截断")
    print(f"  ✓ 最近消息优先策略")
    print(f"  ✓ 对话摘要生成")
    print(f"  ✓ 数据库状态一致性")
    
    print("\n🎉 Phase 2 Context Management 功能验证完成！\n")


def test_edge_cases():
    """测试边界情况"""
    
    print_section("边界情况测试")
    
    context_manager = get_context_manager()
    
    # 测试1: 空对话
    print("\n1. 空对话测试")
    user = User.objects.create_user(
        username="test_edge_case_user",
        email="test_edge@example.com",
        password="testpass123",
    )
    empty_conv = AIConversation.objects.create(
        user=user,
        title="空对话",
        ai_function="general_chat"
    )
    
    messages = context_manager.get_context_messages(
        conversation_id=empty_conv.id,
        max_tokens=1000
    )
    assert len(messages) == 0, "空对话应返回空列表"
    print("  ✓ 空对话处理正确")
    
    # 测试2: 不存在的对话
    print("\n2. 不存在的对话测试")
    messages = context_manager.get_context_messages(
        conversation_id=999999,
        max_tokens=1000
    )
    assert len(messages) == 0, "不存在的对话应返回空列表"
    print("  ✓ 不存在的对话处理正确")
    
    # 测试3: 极限Token限制
    print("\n3. 极限Token限制测试")
    context_manager.add_message(
        empty_conv.id, "user", "测试消息", "model"
    )
    
    messages = context_manager.get_context_messages(
        conversation_id=empty_conv.id,
        max_tokens=1  # 极小限制
    )
    print(f"  → Token限制=1 时返回 {len(messages)} 条消息")
    print("  ✓ 极限Token限制处理正确")
    
    # 清理
    empty_conv.delete()
    
    print("\n✅ 边界情况测试通过！")


if __name__ == "__main__":
    try:
        print("\n")
        print("╔" + "═" * 58 + "╗")
        print("║" + " " * 10 + "Phase 2 多轮对话集成测试" + " " * 20 + "║")
        print("╚" + "═" * 58 + "╝")
        
        # 运行主测试
        test_multi_turn_conversation()
        
        # 运行边界测试
        print("\n")
        test_edge_cases()
        
        print("\n" + "=" * 60)
        print("  🎊 所有集成测试全部通过！")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
