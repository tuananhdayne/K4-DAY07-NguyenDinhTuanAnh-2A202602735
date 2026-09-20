#!/usr/bin/env python3
"""
Format crawled Shopee Category 61 articles strictly to match the template:
Only Return & Refund Policy (Chính sách Trả hàng và Hoàn tiền) - no seller warranty.
"""

import csv
import json
import re
from pathlib import Path
import html2text

DATE_STR = "2026-09-20"

DOC_MAPPING = [
    {
        "aid": 188931,
        "doc_id": "quy-dinh-chung-tra-hang-hoan-tien",
        "title": "Những quy định chung về Trả hàng và Hoàn tiền của Shopee",
        "audience": "buyer",
        "category": "returns-policy",
        "source_url": "https://help.shopee.vn/portal/4/article/188931",
    },
    {
        "aid": 204305,
        "doc_id": "tra-hang-doi-y-khong-con-nhu-cau",
        "title": "Những điều cần biết về Trả hàng do Đổi ý hoặc không còn nhu cầu",
        "audience": "buyer",
        "category": "returns-policy",
        "source_url": "https://help.shopee.vn/portal/4/article/204305",
    },
    {
        "aid": 79465,
        "doc_id": "san-pham-han-che-tra-hang",
        "title": "Sản phẩm hạn chế trả hàng trên Shopee",
        "audience": "buyer",
        "category": "returns-policy",
        "source_url": "https://help.shopee.vn/portal/4/article/79465",
    },
    {
        "aid": 79233,
        "doc_id": "huong-dan-gui-yeu-cau-tra-hang-hoan-tien",
        "title": "Hướng dẫn gửi yêu cầu Trả hàng và Hoàn tiền",
        "audience": "buyer",
        "category": "return-process",
        "source_url": "https://help.shopee.vn/portal/4/article/79233",
    },
    {
        "aid": 79467,
        "doc_id": "huong-dan-chuan-bi-bang-chung-tra-hang",
        "title": "Hướng dẫn chuẩn bị bằng chứng khi yêu cầu Trả hàng và Hoàn tiền",
        "audience": "buyer",
        "category": "return-process",
        "source_url": "https://help.shopee.vn/portal/4/article/79467",
    },
    {
        "aid": 79258,
        "doc_id": "cam-nang-tra-hang-hoan-tien",
        "title": "Cẩm nang Trả hàng và Hoàn tiền Shopee",
        "audience": "buyer",
        "category": "returns-policy",
        "source_url": "https://help.shopee.vn/portal/4/article/79258",
    },
    {
        "aid": 79298,
        "doc_id": "theo-doi-tinh-trang-tra-hang-hoan-tien",
        "title": "Theo dõi tình trạng Trả hàng và Hoàn tiền trên Shopee",
        "audience": "buyer",
        "category": "order-tracking",
        "source_url": "https://help.shopee.vn/portal/4/article/79298",
    },
    {
        "aid": 190242,
        "doc_id": "quy-trinh-shopee-xu-ly-tra-hang-hoan-tien",
        "title": "Quy trình Shopee xử lý yêu cầu Trả hàng và Hoàn tiền",
        "audience": "buyer",
        "category": "dispute-resolution",
        "source_url": "https://help.shopee.vn/portal/4/article/190242",
    },
    {
        "aid": 189476,
        "doc_id": "theo-doi-van-chuyen-hang-hoan-tra",
        "title": "Cách theo dõi tình trạng vận chuyển hàng hoàn trả",
        "audience": "buyer",
        "category": "shipping-policy",
        "source_url": "https://help.shopee.vn/portal/4/article/189476",
    },
    {
        "aid": 79508,
        "doc_id": "cach-dong-goi-don-hang-hoan-tra",
        "title": "Cách đóng gói đơn hàng hoàn trả",
        "audience": "buyer",
        "category": "shipping-policy",
        "source_url": "https://help.shopee.vn/portal/4/article/79508",
    },
    {
        "aid": 189477,
        "doc_id": "phuong-thuc-gui-hang-va-phi-hoan-tra",
        "title": "Các phương thức gửi hàng hoàn trả và phí hoàn trả",
        "audience": "buyer",
        "category": "shipping-policy",
        "source_url": "https://help.shopee.vn/portal/4/article/189477",
    },
    {
        "aid": 190387,
        "doc_id": "nguoi-ban-de-xuat-hoan-tien-ngay",
        "title": "Hướng dẫn Người mua trả lời đề xuất Hoàn Tiền Ngay của Người bán",
        "audience": "buyer",
        "category": "return-process",
        "source_url": "https://help.shopee.vn/portal/4/article/190387",
    },
    {
        "aid": 189473,
        "doc_id": "thoi-gian-va-cach-kiem-tra-tien-hoan",
        "title": "Thời gian nhận tiền hoàn và cách kiểm tra tiền hoàn trên Shopee",
        "audience": "buyer",
        "category": "refund-policy",
        "source_url": "https://help.shopee.vn/portal/4/article/189473",
    },
    {
        "aid": 164831,
        "doc_id": "kiem-tra-tien-hoan-spaylater",
        "title": "Làm sao để kiểm tra tiền đã hoàn vào SPayLater hay chưa",
        "audience": "buyer",
        "category": "refund-policy",
        "source_url": "https://help.shopee.vn/portal/4/article/164831",
    },
]


def clean_html(raw_html: str) -> str:
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.ignore_images = False
    converter.body_width = 0
    converter.single_line_break = False

    text = converter.handle(raw_html)
    # Unescape numbered list headings like "1\. " to "1. "
    text = re.sub(r'(\d+)\\\.', r'\1.', text)
    # Remove empty bold markdown artifacts
    text = re.sub(r'\*\*\s*\*\*', '', text)
    # Clean redundant blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def build_markdown(meta: dict, body: str) -> str:
    frontmatter = f"""---
doc_id: {meta['doc_id']}
title: {meta['title']}
audience: {meta['audience']}
category: {meta['category']}
language: vi
source_url: {meta['source_url']}
retrieved_at: {DATE_STR}
document_version: "not-stated"
---

# {meta['title']}

{body}
"""
    return frontmatter


def process_target_dir(target_dir: Path):
    target_dir.mkdir(parents=True, exist_ok=True)
    manifest_records = []

    # Clean old non-standard or seller files if they exist in target_dir
    seller_file = target_dir / "seller-warranty-policy.md"
    if seller_file.exists():
        seller_file.unlink()
        print(f"[{target_dir.name}] Removed {seller_file.name}")

    for item in DOC_MAPPING:
        aid = item["aid"]
        json_file = Path("data_craw/raw_json") / f"article_{aid}.json"
        if not json_file.exists():
            print(f"Skipping {aid}, json not found")
            continue

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        raw_html = data.get("content") or ""
        body = clean_html(raw_html)

        file_name = f"{item['doc_id']}.md"
        out_path = target_dir / file_name

        content = build_markdown(item, body)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

        rel_path = f"{target_dir.name}/{file_name}" if target_dir.name != "ecommerce" else f"data/ecommerce/{file_name}"
        manifest_records.append({
            "doc_id": item["doc_id"],
            "file_path": rel_path,
            "title": item["title"],
            "source_url": item["source_url"],
            "retrieved_at": DATE_STR,
            "document_version": "not-stated",
            "license_or_permission": "public-source"
        })
        print(f"[{target_dir.name}] Saved {file_name}")

    # Write sources.csv
    csv_file = target_dir / "sources.csv"
    fieldnames = ["doc_id", "file_path", "title", "source_url", "retrieved_at", "document_version", "license_or_permission"]
    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in manifest_records:
            writer.writerow(rec)
    print(f"[{target_dir.name}] Saved {csv_file} with {len(manifest_records)} records")


def main():
    # 1. Update data_craw/
    print("=== Processing data_craw ===")
    process_target_dir(Path("data_craw"))

    # 2. Update data/ecommerce/
    print("\n=== Processing data/ecommerce ===")
    process_target_dir(Path("data/ecommerce"))

    # Update data_craw/README.md
    readme_path = Path("data_craw/README.md")
    with open(Path("data_craw/sources.csv"), "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    readme_content = f"""# Dữ Liệu Shopee Help Center: Chính Sách Trả Hàng & Hoàn Tiền

- **Chuyên mục gốc:** [Shopee Help Center - Trả Hàng & Hoàn Tiền (Category 61)](https://help.shopee.vn/portal/4/category/61-Tr%25E1%25BA%25A3-H%25C3%25A0ng-Ho%25C3%25A0n-Ti%25E1%25BB%2581n/)
- **Cấu trúc chuẩn theo template:** `data/ecommerce/` & `docs/DATA_COLLECTION.md`
- **Ngày cập nhật (`retrieved_at`):** {DATE_STR}
- **Tổng số tài liệu:** {len(reader)} tài liệu (100% thuộc chính sách Trả hàng & Hoàn tiền)

---

## 1. Cấu Trúc YAML Frontmatter Chuẩn Mẫu

Mỗi file Markdown `.md` tuân thủ chính xác template mẫu:

```yaml
---
doc_id: <doc_id trùng tên file>
title: <Tên tài liệu>
audience: buyer
category: returns-policy
language: vi
source_url: <URL nguồn công khai>
retrieved_at: {DATE_STR}
document_version: "not-stated"
---
```

---

## 2. Danh Sách Tài Liệu & Kiểm Kê (sources.csv)

| # | doc_id | Tên tài liệu | Đối tượng (audience) | Phân loại (category) | Nguồn (source_url) |
|---|---|---|:---:|:---:|---|
"""
    for idx, r in enumerate(reader, 1):
        p = Path("data_craw") / f"{r['doc_id']}.md"
        aud = "buyer"
        cat = "returns-policy"
        if p.exists():
            text = p.read_text(encoding="utf-8")
            m_aud = re.search(r"^audience:\s*([^\n]+)", text, re.MULTILINE)
            m_cat = re.search(r"^category:\s*([^\n]+)", text, re.MULTILINE)
            if m_aud: aud = m_aud.group(1).strip()
            if m_cat: cat = m_cat.group(1).strip()
        readme_content += f"| {idx} | `{r['doc_id']}` | {r['title']} | `{aud}` | `{cat}` | [{r['source_url']}]({r['source_url']}) |\n"

    readme_content += """
---

## 3. Đặc Điểm Bộ Dữ Liệu

- **Chủ đề thuần nhất:** Toàn bộ 14 tài liệu đều thuộc chuyên mục Trả Hàng & Hoàn Tiền của Shopee, không chứa dữ liệu ngoài phạm vi (như chính sách bảo hành người bán).
- **Tên file chuẩn:** Chữ thường, không dấu, nối bằng dấu gạch ngang `<doc_id>.md`.
- **Khối metadata:** Đúng chuẩn template `return-refund-policy.md`.
- **Kiểm kê:** File `sources.csv` khớp chính xác 1-1 với 14 file `.md`.
- **Làm sạch:** Giữ lại đầy đủ các mốc thời gian (24h, 15 ngày, 3-5 ngày), các bước thao tác, điều kiện đổi ý, hàng hạn chế trả và bảng phương thức hoàn tiền.
"""
    readme_path.write_text(readme_content, encoding="utf-8")
    print("\nUpdated data_craw/README.md successfully.")


if __name__ == "__main__":
    main()
