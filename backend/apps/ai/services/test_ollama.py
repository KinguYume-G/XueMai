"""
AI客户端测试脚本（支持Groq和Ollama）

使用方法：
cd backend
python apps/ai/services/test_ollama.py
"""

# This is an interactive diagnostic script, not an isolated pytest test module.
__test__ = False

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 设置Django环境
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

# 初始化Django
try:
    import django

    django.setup()
except Exception as e:
    print(f"⚠️ Django初始化失败: {e}")
    print("💡 某些功能可能不可用")

import time


def test_ai_client():
    """测试AI客户端（优先Groq，回退Ollama）"""
    print("=" * 60)
    print("AI客户端测试")
    print("=" * 60)

    # 优先尝试Groq
    print("\n[1] 测试AI客户端初始化...")
    client = None
    use_groq = False

    try:
        # 尝试导入并初始化Groq
        print("  尝试Groq...")
        from apps.ai.services.groq_client import GroqClient

        client = GroqClient()
        print("✅ Groq客户端初始化成功")
        use_groq = True
    except Exception as e:
        print(f"⚠️  Groq不可用: {e}")
        print("  回退到Ollama...")

        try:
            # 回退到Ollama
            from apps.ai.services.ollama_client import OllamaClient

            client = OllamaClient()
            print("✅ Ollama客户端初始化成功")
            use_groq = False
        except Exception as e2:
            print(f"❌ Ollama也失败了: {e2}")
            print("💡 请确认：")
            print("   1. Groq: GROQ_API_KEY已配置在.env")
            print("   2. Ollama: 服务运行中（ollama serve）")
            return False

    # 测试同步聊天
    print(f"\n[2] 测试同步聊天({'Groq' if use_groq else 'Ollama'})...")
    test_question = "用一句话解释微积分的核心概念"

    try:
        messages = [{"role": "user", "content": test_question}]
        result = client.chat(messages)

        print(f"问题: {test_question}")
        print(f"回答: {result['content'][:200]}...")
        print(f"⏱️  响应时间: {result['elapsed_ms']}ms")

        # 性能评估
        if result["elapsed_ms"] < 1500:
            print("✅ 性能优秀（<1.5秒）")
        elif result["elapsed_ms"] < 3000:
            print("⚠️  性能良好（1.5-3秒）")
        elif result["elapsed_ms"] < 5000:
            print("⚠️  性能一般（3-5秒）")
        else:
            print("❌ 性能较差（>5秒）")
            if not use_groq:
                print("💡 建议切换到Groq API获得10倍速度提升")

    except Exception as e:
        print(f"❌ 聊天失败: {e}")
        return False

    # 测试流式聊天
    print(f"\n[3] 测试流式聊天...")
    print("回答: ", end="", flush=True)

    try:
        start = time.time()
        chunk_count = 0
        for chunk in client.stream_chat(messages):
            print(chunk, end="", flush=True)
            chunk_count += 1
        elapsed = int((time.time() - start) * 1000)
        print(f"\n⏱️  流式响应时间: {elapsed}ms（{chunk_count}个chunks）")
        print("✅ 流式聊天正常")
    except Exception as e:
        print(f"\n❌ 流式聊天失败: {e}")
        return False

    return True


def test_rag():
    """测试RAG引擎"""
    print("\n" + "=" * 60)
    print("RAG引擎测试")
    print("=" * 60)

    # 检查测试文档
    test_doc_path = Path(__file__).parent.parent.parent.parent / "test_docs" / "library.txt"

    if not test_doc_path.exists():
        print(f"⚠️  测试文档不存在: {test_doc_path}")
        print("💡 请创建测试文档后再运行RAG测试")
        return

    # 初始化RAG引擎
    print("\n[1] 测试RAG引擎初始化...")
    try:
        from apps.ai.services.rag_engine import RAGEngine

        rag = RAGEngine()
        print("✅ RAG引擎初始化成功")
    except Exception as e:
        print(f"❌ RAG引擎初始化失败: {e}")
        return

    # 测试文档摄取
    print("\n[2] 测试文档摄取...")
    try:
        count = rag.ingest_document(str(test_doc_path), metadata={"source": "图书馆使用指南"})
        print(f"✅ 文档摄取成功: {count} 个chunks")
    except Exception as e:
        print(f"❌ 文档摄取失败: {e}")
        return

    # 测试检索
    print("\n[3] 测试文档检索...")
    try:
        docs = rag.retrieve("如何申请图书馆卡", top_k=3)
        print(f"✅ 检索成功: 找到 {len(docs)} 个相关文档")
        print("\n检索结果预览:")
        for i, doc in enumerate(docs, 1):
            preview = doc.page_content[:100].replace("\n", " ")
            print(f"  [{i}] {preview}...")
    except Exception as e:
        print(f"❌ 检索失败: {e}")
        return

    # 测试完整RAG流程
    print("\n[4] 测试完整RAG查询...")
    try:
        # 初始化AI客户端
        try:
            from apps.ai.services.groq_client import GroqClient

            ai_client = GroqClient()
            print("  使用Groq客户端")
        except:
            from apps.ai.services.ollama_client import OllamaClient

            ai_client = OllamaClient()
            print("  使用Ollama客户端")

        answer = rag.rag_query("如何申请图书馆卡？", ai_client, top_k=3)
        print(f"✅ RAG查询成功\n")
        print(f"问题: 如何申请图书馆卡？")
        print(f"答案:\n{answer}\n")
    except Exception as e:
        print(f"❌ RAG查询失败: {e}")
        import traceback

        traceback.print_exc()


def main():
    """主函数"""
    print("\n🚀 开始AI功能测试...\n")

    # 测试AI客户端
    ai_ok = test_ai_client()

    if not ai_ok:
        print("\n❌ AI客户端测试失败，停止后续测试")
        print("💡 请先解决上述问题")
        return

    # 测试RAG（可选）
    test_rag()

    print("\n" + "=" * 60)
    print("🎉 测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
