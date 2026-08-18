"""
RAG 后端迁移测试脚本

测试 ChromaDB 和 pgvector 两种检索后端的功能和性能对比。
"""

# This legacy benchmark is invoked manually and depends on external services.
__test__ = False

import os
import sys
import time
import django

# 设置 Django 环境
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.conf import settings
from apps.ai.services.rag_engine import RAGEngine


def print_separator(title: str = ""):
    """打印分隔线"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}\n")
    else:
        print(f"{'='*60}\n")


def test_chromadb_retrieval():
    """测试 ChromaDB 检索功能"""
    print_separator("测试 1: ChromaDB 检索功能")
    
    # 临时设置为 chromadb 模式
    original_backend = settings.RAG_VECTOR_BACKEND
    settings.RAG_VECTOR_BACKEND = 'chromadb'
    
    try:
        # 初始化 RAGEngine
        print("初始化 RAGEngine (ChromaDB 模式)...")
        rag = RAGEngine()
        
        # 测试查询
        test_queries = [
            "APU 有哪些课程？",
            "如何申请 APU？",
            "APU 的学费是多少？",
        ]
        
        results = {}
        for query in test_queries:
            print(f"\n查询: {query}")
            start_time = time.time()
            
            docs = rag.retrieve(query, top_k=3)
            
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            print(f"  - 检索到 {len(docs)} 个文档")
            print(f"  - 耗时: {elapsed_ms} ms")
            
            if docs:
                print(f"  - 第一个结果预览: {docs[0].page_content[:100]}...")
            
            results[query] = {
                'docs': docs,
                'count': len(docs),
                'time_ms': elapsed_ms
            }
        
        print_separator()
        print(f"✅ ChromaDB 测试完成")
        print(f"   - 总查询数: {len(test_queries)}")
        print(f"   - 平均耗时: {sum(r['time_ms'] for r in results.values()) / len(results):.0f} ms")
        
        return results
        
    except Exception as e:
        print(f"❌ ChromaDB 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    finally:
        # 恢复原始配置
        settings.RAG_VECTOR_BACKEND = original_backend


def test_pgvector_retrieval():
    """测试 pgvector 检索功能"""
    print_separator("测试 2: pgvector 检索功能")
    
    # 临时设置为 pgvector 模式
    original_backend = settings.RAG_VECTOR_BACKEND
    settings.RAG_VECTOR_BACKEND = 'pgvector'
    
    try:
        # 初始化 RAGEngine
        print("初始化 RAGEngine (pgvector 模式)...")
        rag = RAGEngine()
        
        # 测试查询
        test_queries = [
            "APU 有哪些课程？",
            "如何申请 APU？",
            "APU 的学费是多少？",
        ]
        
        results = {}
        for query in test_queries:
            print(f"\n查询: {query}")
            start_time = time.time()
            
            docs = rag.retrieve(query, top_k=3)
            
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            print(f"  - 检索到 {len(docs)} 个文档")
            print(f"  - 耗时: {elapsed_ms} ms")
            
            if docs:
                print(f"  - 第一个结果预览: {docs[0].page_content[:100]}...")
            
            results[query] = {
                'docs': docs,
                'count': len(docs),
                'time_ms': elapsed_ms
            }
        
        print_separator()
        print(f"✅ pgvector 测试完成")
        print(f"   - 总查询数: {len(test_queries)}")
        print(f"   - 平均耗时: {sum(r['time_ms'] for r in results.values()) / len(results):.0f} ms")
        
        return results
        
    except Exception as e:
        print(f"❌ pgvector 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    finally:
        # 恢复原始配置
        settings.RAG_VECTOR_BACKEND = original_backend


def compare_results(chromadb_results, pgvector_results):
    """对比两种后端的检索结果"""
    print_separator("测试 3: 结果对比分析")
    
    if not chromadb_results or not pgvector_results:
        print("❌ 无法进行对比，某个后端测试失败")
        return
    
    print("📊 性能对比：\n")
    
    for query in chromadb_results.keys():
        chromadb_time = chromadb_results[query]['time_ms']
        pgvector_time = pgvector_results[query]['time_ms']
        
        speedup = chromadb_time / pgvector_time if pgvector_time > 0 else 0
        
        print(f"查询: {query}")
        print(f"  ChromaDB: {chromadb_time} ms")
        print(f"  pgvector: {pgvector_time} ms")
        print(f"  加速比: {speedup:.2f}x {'(pgvector 更快)' if speedup > 1 else '(ChromaDB 更快)'}")
        print()
    
    # 计算平均性能
    avg_chromadb = sum(r['time_ms'] for r in chromadb_results.values()) / len(chromadb_results)
    avg_pgvector = sum(r['time_ms'] for r in pgvector_results.values()) / len(pgvector_results)
    avg_speedup = avg_chromadb / avg_pgvector if avg_pgvector > 0 else 0
    
    print_separator()
    print("📈 平均性能：")
    print(f"  ChromaDB 平均: {avg_chromadb:.0f} ms")
    print(f"  pgvector 平均: {avg_pgvector:.0f} ms")
    print(f"  平均加速比: {avg_speedup:.2f}x")
    
    if avg_speedup > 1:
        print(f"\n✅ pgvector 比 ChromaDB 快 {((avg_speedup - 1) * 100):.0f}%")
    else:
        print(f"\n⚠️ ChromaDB 比 pgvector 快 {((1/avg_speedup - 1) * 100):.0f}%")


def main():
    """主测试流程"""
    print_separator("RAG 后端迁移测试")
    
    print(f"当前配置: RAG_VECTOR_BACKEND = {settings.RAG_VECTOR_BACKEND}")
    print(f"开始测试...\n")
    
    # 测试 ChromaDB
    chromadb_results = test_chromadb_retrieval()
    
    # 测试 pgvector
    pgvector_results = test_pgvector_retrieval()
    
    # 对比结果
    compare_results(chromadb_results, pgvector_results)
    
    print_separator("测试完成")


if __name__ == "__main__":
    main()
