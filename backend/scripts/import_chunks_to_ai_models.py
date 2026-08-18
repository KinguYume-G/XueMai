"""
import_chunks_to_ai_models.py

从 unified_chunks.jsonl 文件读取文本块数据，
并将其导入到 Django 的 AIDocument 和 AIChunk 模型中。

设计为从 Django shell 中调用 run() 函数执行。
"""
import os
import sys
import json
from pathlib import Path
from tqdm import tqdm

# --- Django 环境设置 ---
# 将项目根目录 'backend' 添加到 Python 路径
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

# 在 shell 环境中，Django 已被加载
try:
    from apps.ai.models import AIDocument, AIChunk
except ImportError as e:
    print(f"错误: 无法导入 Django 模型 - {e}")
    print("请确保你在 `backend` 目录下，并使用 `python manage.py shell` 运行此脚本。")
    sys.exit(1)


# --- 文件路径定义 ---
CHUNKS_FILE_PATH = BASE_DIR / "data" / "processed_data" / "chunks" / "unified_chunks.jsonl"


def run():
    """
    主执行函数：读取 JSONL 文件并导入数据到数据库。
    """
    print("--- 开始导入 Chunks 到 AI 模型 ---")
    
    if not CHUNKS_FILE_PATH.exists():
        print(f"错误: 切块文件未找到，请检查路径: {CHUNKS_FILE_PATH}")
        return

    # 1. 逐行读取 JSONL 文件
    with CHUNKS_FILE_PATH.open("r", encoding="utf-8") as f:
        lines = f.readlines()
    
    total_records = len(lines)
    if total_records == 0:
        print("文件为空，没有需要导入的数据。")
        return
        
    print(f"在 {CHUNKS_FILE_PATH.name} 中找到 {total_records} 条记录。")

    # 2. 初始化计数器
    docs_created = 0
    chunks_created = 0
    chunks_skipped = 0

    # 创建一个字典来缓存 AIDocument 实例，避免重复查询数据库
    document_cache = {}

    # 3. 遍历记录并导入数据
    progress_bar = tqdm(lines, total=total_records, desc="导入数据中")
    for line in progress_bar:
        line = line.strip()
        if not line:
            chunks_skipped += 1
            continue
        
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            tqdm.write(f"警告: 解析 JSON 失败，跳过此行: {line[:100]}")
            chunks_skipped += 1
            continue

        # 4. 字段映射和数据提取
        # 从 JSON 中提取 'parent_id' 作为 AIDocument 的唯一标识
        doc_unique_id = data.get("metadata", {}).get("parent_id")
        if not doc_unique_id:
            # 如果没有 parent_id，尝试使用 title 和 source 组合作为备用key
            title = data.get("title", "未知标题")
            source = data.get("source", "未知来源")
            doc_unique_id = f"{title}_{source}"

        chunk_content = data.get("content", "").strip()
        chunk_index = data.get("metadata", {}).get("chunk_index")

        if not chunk_content or chunk_index is None:
            tqdm.write(f"警告: Chunk 内容或索引缺失，跳过记录: doc_id={doc_unique_id}")
            chunks_skipped += 1
            continue

        # 5. 创建或获取 AIDocument
        document = document_cache.get(doc_unique_id)
        if not document:
            try:
                # 准备 AIDocument 的元数据
                doc_metadata = {
                    "source": data.get("source"),
                    "category": data.get("category"),
                    # 可以添加其他你认为有用的文档级元数据
                }
                # 移除值为 None 的键
                doc_metadata = {k: v for k, v in doc_metadata.items() if v is not None}

                document, created = AIDocument.objects.get_or_create(
                    title=data.get("title", "无标题文档"),
                    defaults={
                        'doc_type': 'other',
                        'content': chunk_content, # 将第一个 chunk 的内容作为文档的初始内容
                        'metadata': doc_metadata,
                        # 'source_url' 字段在示例数据中没有，留空
                    }
                )
                document_cache[doc_unique_id] = document
                if created:
                    docs_created += 1
            except Exception as e:
                tqdm.write(f"错误: 创建 AIDocument 失败 (ID: {doc_unique_id}) - {e}")
                chunks_skipped += 1
                continue
        
        # 6. 创建 AIChunk
        try:
            # 准备 AIChunk 的元数据
            chunk_metadata = data.get("metadata", {})
            
            _chunk, created = AIChunk.objects.get_or_create(
                document=document,
                chunk_index=chunk_index,
                defaults={
                    'content': chunk_content,
                    'chunk_metadata': chunk_metadata
                }
            )
            if created:
                chunks_created += 1
            else:
                chunks_skipped += 1

        except Exception as e:
            tqdm.write(f"错误: 创建 AIChunk 失败 (Doc: {document.id}, Index: {chunk_index}) - {e}")
            chunks_skipped += 1
            continue

    # 7. 打印最终结果
    print("\n--- 任务完成 ---")
    print(f"总记录行数: {total_records}")
    print(f"  - 新建 AIDocument: {docs_created}")
    print(f"  - 新建 AIChunk: {chunks_created}")
    print(f"  - 跳过/已存在 的 AIChunk: {chunks_skipped}")
    print("--------------------")

# --- 脚本入口 ---
# 如果直接运行此文件（不推荐），则不会执行
# 设计为在 `manage.py shell` 中手动调用 `run()`
if __name__ == "__main__":
    print("这是一个用于 Django shell 的脚本。")
    print("请通过以下方式运行:")
    print("1. cd backend")
    print("2. python manage.py shell")
    print("3. from scripts import import_chunks_to_ai_models")
    print("4. import_chunks_to_ai_models.run()")
