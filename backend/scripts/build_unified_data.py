"""
把不同来源的文档（目前先是 APU FAQs PDF + APU 官网页面）
整理成统一格式：unified_data.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

BASE_DIR = Path(__file__).resolve().parents[1]

# 已经提取好的 PDF 每页 JSON
APU_FAQS_DIR = BASE_DIR / "data" / "processed_data" / "apu_faqs"

# 之前爬 APU 官网生成的 jsonl（如果暂时没有也没事，会自动跳过）
APU_PAGES_JSONL = BASE_DIR / "data" / "raw_data" / "apu_website" / "apu_pages.jsonl"

# 统一输出
OUTPUT_PATH = BASE_DIR / "data" / "processed_data" / "unified_data.json"


def load_apu_faqs() -> List[Dict[str, Any]]:
    """把 apu_faqs 里的每页 JSON 变成统一结构"""
    docs: List[Dict[str, Any]] = []

    if not APU_FAQS_DIR.exists():
        print(f"[WARN] APU_FAQS_DIR not found: {APU_FAQS_DIR}")
        return docs

    pdf_json_files = sorted(APU_FAQS_DIR.glob("*.json"))
    print(f"[INFO] Found {len(pdf_json_files)} pdf-page-json files in {APU_FAQS_DIR}")

    for pdf_json in pdf_json_files:
        with pdf_json.open("r", encoding="utf-8") as f:
            pages = json.load(f)

        pdf_name = pdf_json.stem + ".pdf"

        for page in pages:
            page_num = int(page.get("page", 0))
            content = (page.get("content") or "").strip()
            if not content:
                continue

            doc_id = f"apu_faqs_{pdf_json.stem}_p{page_num:03d}"

            docs.append(
                {
                    "id": doc_id,
                    "source": "APU Brochure",
                    "category": "faq_brochure",
                    "title": pdf_json.stem,  # 先用文件名做标题
                    "content": content,
                    "metadata": {
                        "pdf_name": pdf_name,
                        "page": page_num,
                    },
                }
            )

    return docs


def load_apu_pages() -> List[Dict[str, Any]]:
    """（可选）把 apu_pages.jsonl 也并进来"""
    docs: List[Dict[str, Any]] = []

    if not APU_PAGES_JSONL.exists():
        print(f"[INFO] apu_pages.jsonl not found, skip website pages.")
        return docs

    with APU_PAGES_JSONL.open("r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)

            content = (
                data.get("content")
                or data.get("text")
                or ""
            )
            content = str(content).strip()
            if not content:
                continue

            title = data.get("title") or data.get("url") or "APU page"

            doc_id = f"apu_page_{idx:04d}"

            docs.append(
                {
                    "id": doc_id,
                    "source": "APU官网",
                    "category": "website",
                    "title": title,
                    "content": content,
                    "metadata": {
                        "url": data.get("url"),
                        "last_updated": data.get("last_updated"),
                    },
                }
            )

    return docs


def main() -> None:
    all_docs: List[Dict[str, Any]] = []

    # 1) PDF FAQs
    all_docs.extend(load_apu_faqs())

    # 2) 官网页面（有就加，没有就算了）
    all_docs.extend(load_apu_pages())

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(all_docs, f, ensure_ascii=False, indent=2)

    print(f"[DONE] Saved {len(all_docs)} docs to {OUTPUT_PATH.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
