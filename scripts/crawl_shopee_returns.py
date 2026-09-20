#!/usr/bin/env python3
"""
Crawler for Shopee Help Center Category 61: Trả Hàng & Hoàn Tiền
(https://help.shopee.vn/portal/4/category/61-Tr%25E1%25BA%25A3-H%25C3%25A0ng-Ho%25C3%25A0n-Ti%25E1%25BB%2581n/)

Fetches all subcategories, articles, full details, and converts HTML to Markdown
with standard YAML frontmatter for RAG / Embedding / Chunking experiments.
"""

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import html2text

FRONTEND_ID = 4
CATEGORY_ID = 61
CATEGORY_URL = "https://help.shopee.vn/portal/4/category/61-Tr%25E1%25BA%25A3-H%25C3%25A0ng-Ho%25C3%25A0n-Ti%25E1%25BB%2581n/"
BASE_API = "https://help.shopee.vn/api/inhouse/hc/mobile/v1"
RETRIEVED_AT = datetime.now().strftime("%Y-%m-%d")

OUTPUT_DIR = Path("data_craw")
RAW_JSON_DIR = OUTPUT_DIR / "raw_json"
BY_CAT_DIR = OUTPUT_DIR / "by_category"


def run_curl(url: str) -> dict:
    """Fetch URL using curl to avoid TLS 1.3 / OpenSSL environment issues."""
    cmd = [
        "curl",
        "-s",
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "-H", "Accept: application/json, text/plain, */*",
        "-H", "Referer: https://help.shopee.vn/portal/4/",
        url,
    ]
    for attempt in range(3):
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            try:
                return json.loads(res.stdout)
            except json.JSONDecodeError:
                pass
        time.sleep(1)
    raise RuntimeError(f"Failed to fetch {url}")


def vietnamese_slugify(text: str) -> str:
    s = text.lower()
    # Normalize Vietnamese characters
    s = re.sub(r"[àáạảãâầấậẩẫăằắặẳẵ]", "a", s)
    s = re.sub(r"[èéẹẻẽêềếệểễ]", "e", s)
    s = re.sub(r"[ìíịỉĩ]", "i", s)
    s = re.sub(r"[òóọỏõôồốộổỗơờớợởỡ]", "o", s)
    s = re.sub(r"[ùúụủũưừứựửữ]", "u", s)
    s = re.sub(r"[ỳýỵỷỹ]", "y", s)
    s = re.sub(r"[đ]", "d", s)
    # Remove special punctuation
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[\s-]+", "-", s).strip("-")
    return s[:60] or "article"


def html_to_clean_markdown(html_content: str) -> str:
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.ignore_images = False
    converter.body_width = 0
    converter.single_line_break = False
    
    md = converter.handle(html_content)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip()


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_JSON_DIR.mkdir(parents=True, exist_ok=True)
    BY_CAT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[*] Fetching categories from Shopee Help Center (Frontend ID: {FRONTEND_ID})...")
    cat_api_url = f"{BASE_API}/categories?frontend_id={FRONTEND_ID}"
    cat_data = run_curl(cat_api_url)

    # Save categories raw JSON
    with open(RAW_JSON_DIR / "categories.json", "w", encoding="utf-8") as f:
        json.dump(cat_data, f, ensure_ascii=False, indent=2)

    cat_61 = None
    for c in cat_data.get("dir_info", []):
        if c.get("id") == CATEGORY_ID:
            cat_61 = c
            break

    if not cat_61:
        print(f"[!] Category {CATEGORY_ID} not found!")
        sys.exit(1)

    print(f"[+] Found Category: {cat_61.get('category_name')} (ID: {cat_61.get('id')})")
    subcategories = cat_61.get("sub_dir_info", [])
    print(f"[+] Found {len(subcategories)} subcategories:")
    for idx, sub in enumerate(subcategories, 1):
        print(f"    {idx}. [{sub.get('id')}] {sub.get('category_name')}")

    # Track all articles
    articles_map = {}
    articles_subcat = {}

    for sub_idx, sub in enumerate(subcategories, 1):
        sub_id = sub.get("id")
        sub_name = sub.get("category_name")
        sub_slug = f"{sub_idx:02d}_{vietnamese_slugify(sub_name)}"

        print(f"\n[*] Fetching articles for subcategory [{sub_id}] {sub_name}...")
        sub_api_url = f"{BASE_API}/categories/articles?category_id={sub_id}&frontend_id={FRONTEND_ID}&page=1&size=100"
        sub_data = run_curl(sub_api_url)

        with open(RAW_JSON_DIR / f"subcategory_{sub_id}.json", "w", encoding="utf-8") as f:
            json.dump(sub_data, f, ensure_ascii=False, indent=2)

        items = sub_data.get("articles") or []
        print(f"    Total items: {len(items)}")

        for art in items:
            aid = art.get("id")
            articles_map[aid] = art
            articles_subcat[aid] = {
                "sub_id": sub_id,
                "sub_name": sub_name,
                "sub_slug": sub_slug,
            }

    # Additional articles under category 61 that may be direct or legacy
    additional_cat61_ids = [79137, 79061, 79131]
    for aid in additional_cat61_ids:
        if aid not in articles_map:
            print(f"[*] Checking additional Category 61 article [{aid}]...")
            try:
                art_detail = run_curl(f"{BASE_API}/article?id={aid}&frontend_id={FRONTEND_ID}")
                cat_info = art_detail.get("full_category_info") or {}
                if cat_info.get("category_id") == CATEGORY_ID:
                    sub_info = cat_info.get("sub_category") or {}
                    sub_id = sub_info.get("category_id", 0)
                    sub_name = sub_info.get("name", "Quy định bổ sung")
                    articles_map[aid] = {"id": aid, "title": art_detail.get("title")}
                    articles_subcat[aid] = {
                        "sub_id": sub_id,
                        "sub_name": sub_name,
                        "sub_slug": f"extra_{vietnamese_slugify(sub_name)}",
                    }
                    print(f"    Added article [{aid}] {art_detail.get('title')}")
            except Exception as e:
                print(f"    Could not fetch article [{aid}]: {e}")

    print(f"\n[+] Total distinct articles to crawl: {len(articles_map)}")

    articles_summary = []

    for aid, art_stub in sorted(articles_map.items()):
        sub_info = articles_subcat[aid]
        sub_slug = sub_info["sub_slug"]
        sub_name = sub_info["sub_name"]
        sub_id = sub_info["sub_id"]

        sub_folder = BY_CAT_DIR / sub_slug
        sub_folder.mkdir(parents=True, exist_ok=True)

        print(f"[*] Downloading article [{aid}]...")
        art_url = f"{BASE_API}/article?id={aid}&frontend_id={FRONTEND_ID}"
        art_detail = run_curl(art_url)

        with open(RAW_JSON_DIR / f"article_{aid}.json", "w", encoding="utf-8") as f:
            json.dump(art_detail, f, ensure_ascii=False, indent=2)

        title = art_detail.get("title") or art_stub.get("title") or f"Article {aid}"
        raw_html = art_detail.get("content") or ""
        markdown_body = html_to_clean_markdown(raw_html)

        source_url = f"https://help.shopee.vn/portal/4/article/{aid}"
        title_slug = vietnamese_slugify(title)
        filename = f"{aid}-{title_slug}.md"

        char_count = len(markdown_body)
        word_count = len(markdown_body.split())

        # Construct YAML frontmatter
        doc_id = f"shopee-returns-{aid}"
        frontmatter = f"""---
doc_id: "{doc_id}"
article_id: {aid}
title: "{title.replace('"', '\\"')}"
audience: "buyer"
category: "Trả Hàng & Hoàn Tiền"
category_id: {CATEGORY_ID}
sub_category: "{sub_name}"
sub_category_id: {sub_id}
language: "vi"
source_url: "{source_url}"
retrieved_at: "{RETRIEVED_AT}"
document_version: "1.0"
character_count: {char_count}
word_count: {word_count}
---

# {title}

{markdown_body}
"""

        # Write to root data_craw/
        flat_file = OUTPUT_DIR / filename
        with open(flat_file, "w", encoding="utf-8") as f:
            f.write(frontmatter)

        # Write to by_category/
        cat_file = sub_folder / filename
        with open(cat_file, "w", encoding="utf-8") as f:
            f.write(frontmatter)

        print(f"    Saved: {filename} ({char_count:,} chars, {word_count:,} words)")

        articles_summary.append({
            "doc_id": doc_id,
            "article_id": aid,
            "title": title,
            "sub_category": sub_name,
            "sub_category_id": sub_id,
            "source_url": source_url,
            "char_count": char_count,
            "word_count": word_count,
            "filename": filename,
            "path": str(flat_file),
            "by_category_path": str(cat_file),
        })

    # Save summary metadata JSON
    with open(OUTPUT_DIR / "metadata.json", "w", encoding="utf-8") as f:
        json.dump({
            "source": CATEGORY_URL,
            "category_name": "Trả Hàng & Hoàn Tiền",
            "category_id": CATEGORY_ID,
            "frontend_id": FRONTEND_ID,
            "retrieved_at": RETRIEVED_AT,
            "total_articles": len(articles_summary),
            "articles": articles_summary
        }, f, ensure_ascii=False, indent=2)

    # Generate README.md
    readme_content = f"""# Dữ Liệu Shopee Help Center: Trả Hàng & Hoàn Tiền

- **Nguồn chuyên mục:** [{CATEGORY_URL}]({CATEGORY_URL})
- **Frontend Portal:** Shopee Người mua (Portal 4)
- **Category ID:** {CATEGORY_ID} (Trả Hàng & Hoàn Tiền)
- **Ngày thu thập (`retrieved_at`):** {RETRIEVED_AT}
- **Tổng số tài liệu:** {len(articles_summary)} bài viết

---

## 1. Cấu Trúc Thư Mục `data_craw/`

```text
data_craw/
├── *.md                    # Toàn bộ {len(articles_summary)} bài viết dạng Markdown phẳng (sẵn sàng nạp RAG/Chunking)
├── by_category/            # Phân nhóm bài viết theo từng danh mục con
│   ├── 01_nhung-quy-dinh-chung-ve-tra-hang-hoan-tien/
│   ├── 02_gui-yeu-cau-tra-hang/
│   ├── 03_theo-doi-yeu-cau-tra-hang/
│   ├── 04_shopee-xem-xet/
│   ├── 05_tra-hang/
│   ├── 06_nguoi-ban-khieu-nai/
│   └── 07_hoan-tien/
├── raw_json/               # Toàn bộ dữ liệu phản hồi JSON gốc từ API Shopee
├── metadata.json           # Danh sách và siêu dữ liệu tổng hợp
└── README.md               # Tài liệu này
```

---

## 2. Bảng Thống Kê Tài Liệu (Exercise 3.0 Manifest)

| # | ID | Tên tài liệu | Danh mục con | Nguồn (Source URL) | Số ký tự | Số từ | File |
|---|---|---|---|---|---:|---:|---|
"""

    for idx, item in enumerate(articles_summary, 1):
        readme_content += (
            f"| {idx} | {item['article_id']} | {item['title']} | {item['sub_category']} | "
            f"[{item['source_url']}]({item['source_url']}) | {item['char_count']:,} | "
            f"{item['word_count']:,} | `{item['filename']}` |\n"
        )

    readme_content += f"""
---

## 3. Cấu Trúc Siêu Dữ Liệu (Metadata Schema) Mỗi Tài Liệu

Mỗi file `.md` đều chứa phần YAML frontmatter ở đầu file:

```yaml
---
doc_id: "shopee-returns-<id>"
article_id: <id>
title: "<Tiêu đề bài viết>"
audience: "buyer"
category: "Trả Hàng & Hoàn Tiền"
category_id: 61
sub_category: "<Tên danh mục con>"
sub_category_id: <id danh mục con>
language: "vi"
source_url: "https://help.shopee.vn/portal/4/article/<id>"
retrieved_at: "{RETRIEVED_AT}"
document_version: "1.0"
character_count: <số ký tự>
word_count: <số từ>
---
```
"""

    with open(OUTPUT_DIR / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"\n[✓] Finished successfully! Crawled {len(articles_summary)} articles to '{OUTPUT_DIR}'.")


if __name__ == "__main__":
    main()
