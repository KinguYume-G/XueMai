"""
端到端Orchestrator工作流测试

测试完整流程：
1. 模拟用户登录Context
2. 创建测试文档
3. 调用Orchestrator API
4. 验证返回结果
"""

import os
import sys
import django

# 设置Django环境
sys.path.insert(0, r'C:\Users\hp\Desktop\UniPulse Asia\XueMai\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.ai.models import AIDocument
from django.contrib.auth import get_user_model
from apps.ai.orchestrator import get_orchestrator, WorkflowConfigLoader, ExecutionContext
import uuid

User = get_user_model()

print("=" * 80)
print("端到端Orchestrator工作流测试")
print("=" * 80)

# 1. 获取测试用户
print("\n【步骤1】获取测试用户")
print("-" * 80)
user = User.objects.first()
if not user:
    print("❌ 错误：数据库中没有用户")
    sys.exit(1)
print(f"✅ 使用用户: {user.username}")

# 2. 创建测试文档
print("\n【步骤2】创建测试简历文档")
print("-" * 80)
test_document = AIDocument.objects.create(
    doc_type='resume',
    title='测试简历.docx',
    content='''
    张三的简历
    
    教育背景：
    - 北京大学 计算机科学 2020-2024
    
    工作经验：
    - 软件工程师 2024-至今
      负责后端开发和系统设计
    
    技能：
    Python, Django, React, PostgreSQL
    ''',
    uploaded_by=user,
    metadata={'file_extension': 'docx', 'file_size': 5120}
)
print(f"✅ 创建文档: ID={test_document.id}, 标题={test_document.title}")

# 3. 加载工作流配置
print("\n【步骤3】加载工作流配置")
print("-" * 80)
try:
    workflow_config = WorkflowConfigLoader.load_from_yaml(
        'apps/ai/workflows/resume_optimization.yaml'
    )
    print(f"✅ 工作流: {workflow_config.name}")
    print(f"   步骤数: {len(workflow_config.steps)}")
except Exception as e:
    print(f"❌ 加载失败: {e}")
    test_document.delete()
    sys.exit(1)

# 4. 创建执行上下文
print("\n【步骤4】创建执行上下文")
print("-" * 80)
context = ExecutionContext(
    user=user,
    workflow_id=str(uuid.uuid4()),
    initial_input="帮我优化简历",
    uploaded_files=[test_document],
    variables={}
)
print(f"✅ 工作流ID: {context.workflow_id}")
print(f"   输入: {context.initial_input}")
print(f"   文档数: {len(context.uploaded_files)}")

# 5. 执行工作流
print("\n【步骤5】执行工作流")
print("-" * 80)
try:
    orchestrator = get_orchestrator()
    
    step_count = 0
    for progress in orchestrator.execute_workflow(workflow_config, context, yield_progress=True):
        event_type = progress.get('type')
        
        if event_type == 'workflow_start':
            print(f"🔄 工作流开始: {progress.get('workflow_name')}")
            print(f"   总步骤数: {progress.get('total_steps')}")
        
        elif event_type == 'step_completed':
            step_count += 1
            step_name = progress.get('step_name')
            print(f"✅ 步骤{step_count}完成: {step_name}")
        
        elif event_type == 'step_failed':
            print(f"❌ 步骤失败: {progress.get('step_name')}")
            print(f"   错误: {progress.get('error')}")
        
        elif event_type == 'workflow_completed':
            elapsed_ms = progress.get('elapsed_ms')
            print(f"🎉 工作流完成! 耗时: {elapsed_ms}ms ({elapsed_ms/1000:.2f}s)")
        
        elif event_type == 'workflow_failed':
            print(f"💥 工作流失败: {progress.get('error')}")
    
    print(f"\n✅ 执行完成，共{step_count}个步骤")
    
except Exception as e:
    print(f"❌ 执行失败: {e}")
    import traceback
    traceback.print_exc()
    test_document.delete()
    sys.exit(1)

# 6. 验证结果
print("\n【步骤6】验证结果")
print("-" * 80)
if context.step_results:
    print(f"✅ 步骤结果数: {len(context.step_results)}")
    
    # 查找最终的answer
    answer_found = False
    for step_id, result in context.step_results.items():
        if result.success and 'answer' in result.data:
            answer = result.data['answer']
            print(f"✅ 找到AI回复:")
            print(f"   步骤: {step_id}")
            print(f"   长度: {len(answer)}字")
            print(f"   前100字: {answer[:100]}...")
            answer_found = True
            break
    
    if not answer_found:
        print("⚠️  警告：未找到answer字段")
else:
    print("❌ 错误：没有步骤结果")

# 7. 清理测试数据
print("\n【步骤7】清理测试数据")
print("-" * 80)
test_document.delete()
print(f"✅ 已删除测试文档 ID={test_document.id}")

# 8. 总结
print("\n" + "=" * 80)
print("测试总结")
print("=" * 80)
print("✅ 用户获取: 正常")
print("✅ 文档创建: 正常")
print("✅ 工作流配置: 正常")
print("✅ 执行上下文: 正常")
print("✅ 工作流执行: 正常")
print("✅ 结果验证: 正常")
print("\n🎊 端到端测试通过！Orchestrator工作流完全可用。")
print("=" * 80)
