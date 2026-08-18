"""
从 APU FAQ / Brochure 等 PDF 中提取文本，按页保存成 JSON。

输入目录：
  backend/data/raw_data/faqs/pdfs/*.pdf

输出目录：
  backend/data/processed_data/apu_faqs/*.json
  每个 json 的结构：
  [
    {"page": 1, "content": "..."},
    {"page": 2, "content": "..."},
    ...
  ]
"""

from __future__ import annotations

import json
from pathlib import Path

import pdfplumber

# 项目根目录：.../backend
BASE_DIR = Path(__file__).resolve().parents[1]

RAW_PDF_DIR = BASE_DIR / "data" / "raw_data" / "faqs" / "pdfs"
OUTPUT_DIR = BASE_DIR / "data" / "processed_data" / "apu_faqs"


def extract_pdf_pages(pdf_path: Path) -> list[dict]:
    """读取单个 PDF，返回 [{page: int, content: str}, ...]"""
    pages: list[dict] = []

    with pdfplumber.open(pdf_path) as pdf:
        for idx, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            # 清理一下奇怪字符，并保留换行
            text = text.replace("\x00", "").strip()

            pages.append(
                {
                    "page": idx,
                    "content": text,
                }
            )

    return pages


def main() -> None:
    if not RAW_PDF_DIR.exists():
        raise SystemExit(f"Raw PDF directory not found: {RAW_PDF_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(RAW_PDF_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {RAW_PDF_DIR}")
        return

    print(f"Found {len(pdf_files)} PDFs in {RAW_PDF_DIR}")
    for pdf_path in pdf_files:
        print(f"Processing: {pdf_path.name} ...")

        pages = extract_pdf_pages(pdf_path)

        out_path = OUTPUT_DIR / f"{pdf_path.stem}.json"
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(pages, f, ensure_ascii=False, indent=2)

        print(f"  -> Saved to {out_path.relative_to(BASE_DIR)}")

    print("All done ✅")


if __name__ == "__main__":
    main()
