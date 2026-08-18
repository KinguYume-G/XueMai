"""
把 unified_data.json 里的文档切成 chunks，
输出到 data/processed_data/chunks/unified_chunks.jsonl
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from langchain.text_splitter import RecursiveCharacterTextSplitter

BASE_DIR = Path(__file__).resolve().parents[1]

UNIFIED_DATA_PATH = BASE_DIR / "data" / "processed_data" / "unified_data.json"
CHUNKS_OUTPUT_PATH = BASE_DIR / "data" / "processed_data" / "chunks" / "unified_chunks.jsonl"


def load_unified_docs() -> List[Dict[str, Any]]:
    with UNIFIED_DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def clean_metadata(metadata_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    清理元数据:
    1. 移除所有 None 值
    2. 只保留 ChromaDB 支持的类型 (str, int, float, bool)
    3. 其他复杂类型统一转成字符串
    """
    cleaned: Dict[str, Any] = {}
    for key, value in metadata_dict.items():
        if value is None:
            # 跳过 None
            continue
        if isinstance(value, (str, int, float, bool)):
            cleaned[key] = value
        else:
            # list / dict / 其他类型 -> str
            cleaned[key] = str(value)
    return cleaned


def main() -> None:
    docs = load_unified_docs()
    print(f"[INFO] Loaded {len(docs)} docs from unified_data.json")

    CHUNKS_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # 这里可以以后再调参数，现在先用一个比较稳的配置
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,      # 大约 500 汉字 / 1000 英文字符
        chunk_overlap=200,    # 20% 重叠
        separators=["\n\n", "\n", "。", "！", "？", "!", "?", "，", ",", " "],
    )

    total_chunks = 0

    with CHUNKS_OUTPUT_PATH.open("w", encoding="utf-8") as out_f:
        for doc in docs:
            text = (doc.get("content") or "").strip()
            if not text:
                continue

            chunks = splitter.split_text(text)

            # 每个原始文档的基础 metadata
            base_metadata: Dict[str, Any] = {
                **(doc.get("metadata") or {}),
                "parent_id": doc.get("id"),
            }

            for idx, chunk_text in enumerate(chunks):
                chunk_id = f"{doc['id']}_chunk_{idx:03d}"

                # 这一块 chunk 自己的原始 metadata
                raw_chunk_metadata: Dict[str, Any] = {
                    **base_metadata,
                    "chunk_index": idx,
                }

                # ✅ 在这里做清洗，去掉 None / 复杂类型
                chunk_metadata = clean_metadata(raw_chunk_metadata)

                chunk_obj = {
                    "id": chunk_id,
                    "source": doc.get("source"),
                    "category": doc.get("category"),
                    "title": doc.get("title"),
                    "content": chunk_text,
                    "metadata": chunk_metadata,
                }

                out_f.write(json.dumps(chunk_obj, ensure_ascii=False) + "\n")
                total_chunks += 1

    print(f"[DONE] Wrote {total_chunks} chunks to {CHUNKS_OUTPUT_PATH.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
