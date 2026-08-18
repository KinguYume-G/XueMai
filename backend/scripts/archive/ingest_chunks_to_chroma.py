"""
把 unified_chunks.jsonl 里的 chunks 写入 Chroma 向量库
使用 Ollama Embeddings (简单稳定)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping
import time

from langchain.docstore.document import Document
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

BASE_DIR = Path(__file__).resolve().parents[1]

CHUNKS_PATH = BASE_DIR / "data" / "processed_data" / "chunks" / "unified_chunks.jsonl"
CHROMA_DIR = BASE_DIR / "chroma_db" / "apu_faqs"


def sanitize_metadata(md: Mapping[str, Any] | None) -> Dict[str, Any]:
    """
    清理元数据:
    - 移除所有 None
    - 把值统一成 Chroma 支持的基础类型 (str / int / float / bool)
    """
    cleaned: Dict[str, Any] = {}
    if not md:
        return cleaned

    for key, value in md.items():
        if value is None:
            continue
        if isinstance(value, (str, int, float, bool)):
            cleaned[key] = value
        else:
            cleaned[key] = str(value)
    return cleaned


def load_chunks() -> List[Document]:
    """从 unified_chunks.jsonl 读取所有 chunk，转换为 LangChain Document 列表"""
    print("[INFO] 开始加载 chunks...")
    documents: List[Document] = []

    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(f"Chunks file not found: {CHUNKS_PATH}")

    with CHUNKS_PATH.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                data: Dict[str, Any] = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"[WARNING] 第 {line_num} 行 JSON 解析失败: {e}")
                continue

            content = (data.get("content") or "").strip()
            if not content:
                continue

            # 统一把 metadata 合并到一个 dict，再一次性清洗
            raw_meta = {
                **(data.get("metadata") or {}),
                "doc_id": data.get("id"),
                "source": data.get("source"),
                "category": data.get("category"),
                "title": data.get("title"),
            }
            metadata = sanitize_metadata(raw_meta)

            documents.append(
                Document(
                    page_content=content,
                    metadata=metadata,
                )
            )
            
            # 每 500 个打印一次进度
            if line_num % 500 == 0:
                print(f"[LOADING] 已读取 {line_num} 行...")

    print(f"[INFO] ✅ 成功加载 {len(documents)} 个 chunk 文档.")
    return documents


def main() -> None:
    print("=" * 60)
    print("开始导入 Chunks 到 ChromaDB")
    print("=" * 60)
    
    # 1. 加载文档
    docs = load_chunks()
    
    if not docs:
        print("[ERROR] 没有加载到任何文档!")
        return

    # 2. 初始化 Embeddings - 使用 Ollama
    print("\n[INFO] 正在初始化 Ollama Embeddings (nomic-embed-text)...")
    
    try:
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        # 测试 embedding 是否工作
        print("[INFO] 测试 embedding 功能...")
        test_embed = embeddings.embed_query("test")
        print(f"[INFO] ✅ Embedding 工作正常 (维度: {len(test_embed)})")
    except Exception as e:
        print(f"[ERROR] ❌ Embedding 初始化失败: {e}")
        print("[提示] 请确保 Ollama 正在运行: ollama serve")
        return

    # 3. 创建/连接 ChromaDB
    print(f"\n[INFO] 准备写入 ChromaDB: {CHROMA_DIR}")
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    vectordb = Chroma(
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )

    # 4. 分批导入
    batch_size = 10  # Ollama 用小一点的 batch
    total = len(docs)
    
    print(f"\n[INFO] 开始分批导入，共 {total} 个文档，每批 {batch_size} 个")
    print("-" * 60)

    start_time = time.time()
    
    for start in range(0, total, batch_size):
        batch_start_time = time.time()
        batch = docs[start : start + batch_size]
        
        try:
            vectordb.add_documents(batch)
            batch_time = time.time() - batch_start_time
            current = min(start + batch_size, total)
            progress = (current / total) * 100
            
            # 计算预估剩余时间
            elapsed = time.time() - start_time
            avg_time_per_batch = elapsed / ((start // batch_size) + 1)
            remaining_batches = (total - current) // batch_size
            eta = remaining_batches * avg_time_per_batch
            
            print(f"[BATCH] ✅ {current}/{total} ({progress:.1f}%) - "
                  f"耗时: {batch_time:.2f}s | 预计剩余: {eta:.0f}s")
        except Exception as e:
            print(f"[ERROR] ❌ 批次 {start}-{start+batch_size} 导入失败: {e}")
            raise

    # 5. 持久化
    print("\n[INFO] 正在持久化到磁盘...")
    vectordb.persist()
    
    total_time = time.time() - start_time
    print("=" * 60)
    print(f"✅ [完成] 所有数据已成功导入并持久化!")
    print(f"总耗时: {total_time:.2f} 秒 ({total_time/60:.1f} 分钟)")
    print("=" * 60)


if __name__ == "__main__":
    main()