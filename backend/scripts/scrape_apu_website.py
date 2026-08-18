"""
简单版 APU 官网爬虫
读取 backend/data/raw_data/apu_website/urls.txt
输出 backend/data/raw_data/apu_website/apu_pages.jsonl
"""

import json
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
APU_RAW_DIR = BASE_DIR / "data" / "raw_data" / "apu_website"
URLS_FILE = APU_RAW_DIR / "urls.txt"
OUTPUT_FILE = APU_RAW_DIR / "apu_pages.jsonl"


def clean_text(soup: BeautifulSoup) -> str:
    """去掉脚本、样式、导航等，只保留正文文本"""
    # 删除 script / style / noscript
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # 尝试删除一些导航类区域
    for tag in soup.find_all(["nav", "footer", "header", "aside"]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    # 去掉空行和多余空格
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def fetch_page(url: str) -> dict:
    """请求单个页面并返回结构化数据"""
    print(f"[INFO] Fetching: {url}")
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    content = clean_text(soup)

    return {
        "url": url,
        "title": title,
        "content": content,
    }


def main() -> None:
    if not URLS_FILE.exists():
        raise FileNotFoundError(f"URL 列表文件不存在: {URLS_FILE}")

    APU_RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] 读取 URL 列表: {URLS_FILE}")

    urls = [
        line.strip()
        for line in URLS_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    if not urls:
        print("[WARN] urls.txt 里没有任何有效 URL，请先填入官网链接。")
        return

    # 以追加方式写 JSONL，方便以后补爬
    with OUTPUT_FILE.open("a", encoding="utf-8") as f_out:
        for url in urls:
            try:
                page = fetch_page(url)
                json_line = json.dumps(page, ensure_ascii=False)
                f_out.write(json_line + "\n")
                print(f"[OK] Saved page: {page['title'][:40]}...")
            except Exception as e:
                print(f"[ERROR] Failed on {url}: {e}")
            finally:
                # 稍微等一等，避免请求太频繁
                time.sleep(1.0)

    print(f"[DONE] 已写入: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
