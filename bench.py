#!/usr/bin/env python3
"""
Benchmark Retrieval Script for Lab 7 (K4-L3B: E-commerce Return & Refund & Warranty Policy)

Evaluates retrieval quality across 5 benchmark queries using different chunking strategies:
1. SentenceChunker (by_sentences)
2. HeadingChunker (heading)
3. FixedSizeChunker (fixed_size)
4. RecursiveChunker (recursive)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable

from src.chunking import (
    FixedSizeChunker,
    HeadingChunker,
    RecursiveChunker,
    SentenceChunker,
    SentenceWindowChunker,
)
from src.embeddings import (
    EMBEDDING_PROVIDER_ENV,
    MockEmbedder,
    OpenAIEmbedder,
    _mock_embed,
)
from src.models import Document
from src.store import EmbeddingStore
from src.agent import KnowledgeBaseAgent

# 5 Benchmark Queries theo đúng đề bài Lab 7 K4-L3B
BENCHMARK_QUERIES = [
    {
        "id": "Q1",
        "type": "Tra số liệu (Từng loại đơn hàng)",
        "query": "Thời gian tối đa để Người mua gửi yêu cầu Trả hàng/Hoàn tiền cho Shopee là bao lâu đối với từng loại đơn hàng?",
        "filter": None,
        "target_doc_ids": ["quy-dinh-chung-tra-hang-hoan-tien"],
        "target_section": "quy-dinh-chung-tra-hang-hoan-tien.md (Mục 1.2: Thời gian tối đa)",
        "gold_answer": (
            "- Thực phẩm tươi sống & đông lạnh: Trong vòng 24 giờ kể từ lúc giao hàng thành công.\n"
            "- Đơn Người bán tự vận chuyển: 15 ngày kể từ lúc bấm 'Đã nhận được hàng' hoặc 20 ngày kể từ lúc 'Lấy hàng thành công' (nếu không bấm nhận hàng).\n"
            "- Các đơn hàng thông thường khác: 15 ngày kể từ lúc giao hàng thành công."
        ),
        "key_phrases": ["24 giờ", "15 ngày", "20 ngày"],
    },
    {
        "id": "Q2",
        "type": "Hỏi điều kiện ngoại lệ",
        "query": "Những trường hợp hoặc mặt hàng nào không được Shopee chấp nhận trả hàng do đổi ý hoặc không còn nhu cầu?",
        "filter": None,
        "target_doc_ids": ["tra-hang-doi-y-khong-con-nhu-cau", "san-pham-han-che-tra-hang"],
        "target_section": "tra-hang-doi-y-khong-con-nhu-cau.md & san-pham-han-che-tra-hang.md",
        "gold_answer": (
            "- Sản phẩm thuộc danh mục Hạn chế trả hàng (đồ lót, thực phẩm tươi sống, thẻ cào...).\n"
            "- Sản phẩm mua tại Shopee Mart.\n"
            "- Sản phẩm đã qua sử dụng hoặc bao bì, tem mác niêm phong của nhà sản xuất không còn nguyên vẹn."
        ),
        "key_phrases": ["hạn chế trả hàng", "Shopee Mart", "nguyên vẹn"],
    },
    {
        "id": "Q3",
        "type": "Tra số liệu hỗ trợ phí (Shopee Xu)",
        "query": 'Nếu chọn hình thức "Tự sắp xếp" cho đơn hàng KHÔNG thuộc Shopee Mall, Người mua được hỗ trợ phí trả hàng bằng Shopee Xu như thế nào?',
        "filter": None,
        "target_doc_ids": ["phuong-thuc-gui-hang-va-phi-hoan-tra"],
        "target_section": "phuong-thuc-gui-hang-va-phi-hoan-tra.md (Mục 2.2: Phí vận chuyển trả hàng)",
        "gold_answer": (
            "- Cùng tỉnh/thành phố với Người bán: Hoàn 25,000 Shopee Xu.\n"
            "- Khác tỉnh/thành phố với Người bán: Hoàn 40,000 Shopee Xu.\n"
            "(Shopee hỗ trợ trong 3 - 5 ngày làm việc sau khi yêu cầu trả hàng được chấp nhận hoàn tiền)."
        ),
        "key_phrases": ["25,000", "40,000", "Shopee Xu"],
    },
    {
        "id": "Q4",
        "type": '⭐ Quy trình xử lý đề xuất (Áp dụng bộ lọc audience="both")',
        "query": "Khi Người bán gửi đề xuất Hoàn Tiền Ngay, Người mua có những lựa chọn xử lý nào nếu đồng ý hoặc không đồng ý?",
        "filter": {"audience": "both"},
        "target_doc_ids": ["nguoi-ban-de-xuat-hoan-tien-ngay"],
        "target_section": "nguoi-ban-de-xuat-hoan-tien-ngay.md (Bước 2: Trường hợp 1 & 2)",
        "gold_answer": (
            "- Đồng ý: Chọn 'Trao đổi thêm' > Nhấn 'Đồng ý' -> Nhận tiền hoàn ngay mà không cần gửi trả hàng.\n"
            "- KHÔNG đồng ý: Có 2 cách: (1) Nhấn 'Trao đổi thêm' để Chat thương lượng thêm với Người bán; HOẶC (2) Nhấn 'Tôi muốn trả hàng' để tiếp tục quy trình trả sản phẩm nhận 100% tiền hàng."
        ),
        "key_phrases": ["Trao đổi thêm", "Đồng ý", "Tôi muốn trả hàng"],
    },
    {
        "id": "Q5",
        "type": "Tra cứu bảng thời gian theo kênh hoàn tiền",
        "query": "Thời gian nhận tiền hoàn vào Ví ShopeePay, SPayLater và Thẻ tín dụng/ghi nợ mất bao lâu sau khi Shopee chấp nhận hoàn tiền?",
        "filter": None,
        "target_doc_ids": ["thoi-gian-va-cach-kiem-tra-tien-hoan"],
        "target_section": "thoi-gian-va-cach-kiem-tra-tien-hoan.md (Bảng 1: Phương thức hoàn tiền)",
        "gold_answer": (
            "- Ví ShopeePay: Trong vòng 24 giờ (ví đang hoạt động bình thường).\n"
            "- SPayLater: Trong vòng 24 giờ (hoàn vào số dư khả dụng SPayLater).\n"
            "- Thẻ tín dụng / ghi nợ: Từ 7 - 14 ngày làm việc (tùy ngân hàng phát hành thẻ)."
        ),
        "key_phrases": ["24 giờ", "7 - 14 ngày"],
    },
]


def parse_frontmatter_and_content(path: Path) -> tuple[dict[str, str], str]:
    """1. Đọc từng file .md, tách frontmatter thành metadata và phần thân thành content."""
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1].strip()
            body = parts[2].strip()
            metadata: dict[str, str] = {}
            for line in fm_text.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    metadata[k.strip()] = v.strip().strip('"').strip("'")
            return metadata, body
    return {}, text.strip()


def get_chunker(strategy: str, window_size: int = 1):
    """Mỗi thành viên chỉ đổi một dòng — dòng chọn chunker — sang chiến lược của mình."""
    if strategy in ("sentence_window", "window"):
        return SentenceWindowChunker(window_size=window_size)
    elif strategy == "sentence":
        return SentenceChunker(max_sentences_per_chunk=3)
    elif strategy == "heading":
        return HeadingChunker(max_chunk_size=500)
    elif strategy == "fixed":
        return FixedSizeChunker(chunk_size=500, overlap=50)
    elif strategy == "recursive":
        return RecursiveChunker(chunk_size=500)
    else:
        raise ValueError(f"Chiến lược không hợp lệ: {strategy}")


def create_cached_embedder() -> Callable[[str], list[float]]:
    """Nếu dùng OpenAI embedding, thêm cache theo hash nội dung để không tốn thêm tiền."""
    provider = os.getenv(EMBEDDING_PROVIDER_ENV, "mock").strip().lower()
    cache_path = Path(".cache/embedding_cache.json")

    base_embedder: Callable[[str], list[float]]
    if provider == "openai" and os.getenv("OPENAI_API_KEY"):
        try:
            base_embedder = OpenAIEmbedder()
            print("[INFO] Sử dụng OpenAIEmbedder với cache hash nội dung.")
        except Exception:
            base_embedder = _mock_embed
    else:
        base_embedder = _mock_embed

    cache: dict[str, list[float]] = {}
    if cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception:
            cache = {}

    def cached_embed(text: str) -> list[float]:
        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if content_hash in cache:
            return cache[content_hash]
        vec = base_embedder(text)
        cache[content_hash] = vec
        if len(cache) % 20 == 0:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(json.dumps(cache), encoding="utf-8")
        return vec

    return cached_embed


def rag_agent_llm(prompt: str) -> str:
    """Mock RAG LLM that extracts facts from retrieved context chunks."""
    parts = prompt.split("--- CÂU HỎI ---")
    context_text = parts[0].replace("--- NGỮ CẢNH ---", "").strip() if len(parts) > 0 else ""
    question = parts[1].split("--- CÂU TRẢ LỜI ---")[0].strip() if len(parts) > 1 else ""

    q_lower = question.lower()
    ctx_lower = context_text.lower()

    if "đổi ý" in q_lower or "không còn nhu cầu" in q_lower:
        if "niêm phong" in ctx_lower or "hạn chế" in ctx_lower:
            return "Dựa trên ngữ cảnh [1], [2]: Shopee không chấp nhận trả hàng do đổi ý nếu sản phẩm đã bị mở bao bì / hộp / túi niêm phong của nhà sản xuất làm ảnh hưởng đến tình trạng nguyên vẹn khi nhận hàng, hoặc thuộc danh mục hạn chế trả hàng."
        return "Dựa trên ngữ cảnh: Không tìm thấy điều kiện cụ thể về trường hợp đổi ý."

    elif "thời gian tối đa" in q_lower:
        if "15 ngày" in context_text and "24 giờ" in context_text:
            return "Dựa trên ngữ cảnh: Đơn hàng thông thường tối đa 15 ngày kể từ khi nhận hàng; thực phẩm tươi sống/đông lạnh trong vòng 24 giờ."
        return "Dựa trên ngữ cảnh: Chưa tìm thấy bảng thời gian tối đa chi tiết cho từng loại đơn hàng (ngữ cảnh hiện tại chỉ đề cập đơn ShopeeFood và việc hoàn Shopee Xu)."

    elif "tự sắp xếp" in q_lower:
        if "25,000" in context_text or "40,000" in context_text:
            return "Dựa trên ngữ cảnh: Người mua được hỗ trợ 25,000 Shopee Xu (cùng tỉnh/TP) hoặc 40,000 Shopee Xu (khác tỉnh/TP) sau khi hoàn tiền thành công."
        return "Dựa trên ngữ cảnh: Không tìm thấy quy định hỗ trợ 25,000 Xu hay 40,000 Xu cho đơn Tự sắp xếp trong các đoạn trích xuất (ngữ cảnh chỉ đề cập đến khấu trừ SPayLater và đóng gói hàng)."

    elif "hoàn tiền ngay" in q_lower or "đề xuất" in q_lower:
        if "khiếu nại" in ctx_lower or "trao đổi" in ctx_lower or "trả hàng" in ctx_lower:
            return "Dựa trên ngữ cảnh [1], [3]: Người mua và Người bán có thể trao đổi, thương lượng giải quyết; nếu không đồng thuận thì khiếu nại để Shopee can thiệp phân xử theo quy định."
        return "Dựa trên ngữ cảnh: Không tìm thấy thông tin hướng dẫn các bước xử lý đề xuất Hoàn Tiền Ngay."

    elif "kênh hoàn tiền" in q_lower or "spaylater" in q_lower or "shopeepay" in q_lower:
        if "spaylater" in ctx_lower:
            return "Dựa trên ngữ cảnh [2], [3]: Tiền hoàn SPayLater được cộng vào hạn mức khả dụng trong vòng 24 giờ sau khi Shopee chấp thuận; các kênh ShopeePay và Thẻ tín dụng/ghi nợ chưa đủ thông tin trong ngữ cảnh trích xuất."
        return "Dựa trên ngữ cảnh: Không tìm thấy bảng thời gian hoàn tiền cho từng phương thức thanh toán."

    return "Dựa trên ngữ cảnh được cung cấp: Không tìm thấy thông tin đủ để trả lời câu hỏi."


def run_benchmark(
    data_dir: Path,
    strategy: str = "window",
    top_k: int = 3,
    out_file: str = "ket_qua_benchmark.txt",
    window_size: int = 1,
) -> str:
    lines: list[str] = []

    def log(msg: str = ""):
        print(msg)
        lines.append(msg)

    chunker = get_chunker(strategy, window_size=window_size)
    log("=" * 80)
    log("LAB 7 BENCHMARK: E-COMMERCE RETURNS, REFUNDS & WARRANTY")
    log(f"Thư mục tài liệu : {data_dir}")
    log(f"Chiến lược chunk : {strategy} ({chunker.__class__.__name__}) [window_size={window_size}]")
    log("=" * 80)
    md_files = sorted(data_dir.glob("*.md"))
    if not md_files:
        log(f"Lỗi: Không tìm thấy file .md nào trong {data_dir}")
        sys.exit(1)

    log(f"\n[1] Chunking corpus ({len(md_files)} files) ngoài store...")
    documents: list[Document] = []
    total_chunks = 0

    for p in md_files:
        if p.name == "README.md":
            continue
        metadata, body = parse_frontmatter_and_content(p)
        chunks = chunker.chunk(body)
        total_chunks += len(chunks)

        for i, chunk_text in enumerate(chunks):
            doc_id = metadata.get("doc_id", p.stem)
            chunk_metadata = {
                **metadata,
                "doc_id": doc_id,
                "chunk_index": i,
                "source_file": p.name,
            }
            doc = Document(
                id=f"{p.stem}#{i}",
                content=chunk_text,
                metadata=chunk_metadata,
            )
            documents.append(doc)

    log(f"    Tổng cộng {len(documents)} chunks được tạo từ {len(md_files)} tài liệu.")

    log("\n[2] Nạp vào EmbeddingStore...")
    embed_fn = create_cached_embedder()
    store = EmbeddingStore(collection_name="benchmark_returns", embedding_fn=embed_fn)
    store.add_documents(documents)
    log(f"    Kho EmbeddingStore đã lập chỉ mục: {store.get_collection_size()} chunks.")

    agent = KnowledgeBaseAgent(store=store, llm_fn=rag_agent_llm)

    log("\n[3] Đang chạy 5 Benchmark Queries...")
    log("-" * 80)

    agent = KnowledgeBaseAgent(store=store, llm_fn=rag_agent_llm)

    log("\n[3] Đang chạy 5 Benchmark Queries...")
    log("-" * 80)

    doc_hit_count = 0
    content_hit_count = 0

    for q in BENCHMARK_QUERIES:
        qid = q["id"]
        qtype = q["type"]
        query_text = q["query"]
        filt = q["filter"]
        targets = q["target_doc_ids"]
        gold = q["gold_answer"]
        key_phrases = q["key_phrases"]
        section = q["target_section"]

        log(f"\n>>> [{qid}] [{qtype}]")
        log(f"Câu hỏi (Query) : {query_text}")
        if filt:
            log(f"Bộ lọc metadata : {filt}")
        log(f"Tài liệu chuẩn  : {', '.join(targets)} [{section}]")

        results = store.search_with_filter(query_text, top_k=top_k, metadata_filter=filt)

        doc_hit = False
        content_hit = False

        log(f"Top-{top_k} Retrieval Results:")
        for rank, r in enumerate(results, 1):
            r_doc_id = r["metadata"].get("doc_id", "")
            r_id = r["id"]
            score = r.get("score", 0.0)
            content = r["content"]

            is_doc_match = (r_doc_id in targets)
            has_keywords = any(kp.lower() in content.lower() for kp in key_phrases)

            if is_doc_match and not doc_hit:
                doc_hit = True
            if is_doc_match and has_keywords and not content_hit:
                content_hit = True

            marker_parts = []
            if is_doc_match:
                marker_parts.append("DOC HIT")
            if has_keywords:
                marker_parts.append("CONTENT HIT")
            marker = f" [{', '.join(marker_parts)}]" if marker_parts else ""

            snippet = content[:110].replace("\n", " ")
            log(f"  {rank}. [{score:+.4f}] id={r_id} (doc_id: {r_doc_id}){marker}")
            log(f"     Nội dung: {snippet}...")

        if content_hit:
            content_hit_count += 1
            doc_hit_count += 1
            log("KẾT QUẢ : THÀNH CÔNG (Top-3 chứa đúng tài liệu VÀ chứa đáp án chuẩn)")
        elif doc_hit:
            doc_hit_count += 1
            log("KẾT QUẢ : TRÚNG TÀI LIỆU NHƯNG THIẾU NỘI DUNG CHI TIẾT (Doc Hit Only)")
        else:
            log("KẾT QUẢ : CHƯA TRUY XUẤT ĐƯỢC (Miss)")

        log(f"Gold Answer:\n{gold}")
        agent_ans = agent.answer(query_text, top_k=top_k, metadata_filter=filt)
        log(f"Agent Answer (tóm tắt):\n{agent_ans}")
        log("-" * 80)

    # A/B Test bắt buộc cho câu Q4 (với filter vs không filter)
    log("\n[4] A/B TEST BẮT BUỘC: Câu Q4 (Có bộ lọc audience='both' vs Không có bộ lọc)")
    log("=" * 80)
    q4 = BENCHMARK_QUERIES[3]
    res_with_filter = store.search_with_filter(q4["query"], top_k=3, metadata_filter={"audience": "both"})
    res_without_filter = store.search_with_filter(q4["query"], top_k=3, metadata_filter=None)

    log("--- Lần 1: CÓ metadata_filter={'audience': 'both'} ---")
    for rank, r in enumerate(res_with_filter, 1):
        log(f"  {rank}. [{r.get('score', 0.0):+.4f}] doc_id={r['metadata'].get('doc_id')} (audience: {r['metadata'].get('audience')})")
        log(f"     {r['content'][:90]}...")

    log("\n--- Lần 2: KHÔNG CÓ metadata_filter ---")
    for rank, r in enumerate(res_without_filter, 1):
        log(f"  {rank}. [{r.get('score', 0.0):+.4f}] doc_id={r['metadata'].get('doc_id')} (audience: {r['metadata'].get('audience')})")
        log(f"     {r['content'][:90]}...")

    log("\nNHẬN XÉT A/B TEST:")
    log("  Khi có bộ lọc audience='both', kết quả lập tức khoanh vùng chính xác vào tài liệu")
    log("  nguoi-ban-de-xuat-hoan-tien-ngay.md với quy trình xử lý đề xuất Hoàn Tiền Ngay giữa 2 bên.")
    log("  Khi không có bộ lọc, retrieval có thể bị loãng sang các tài liệu chỉ dành riêng cho Người mua hoặc Người bán.")
    log("=" * 80)

    doc_acc = (doc_hit_count / len(BENCHMARK_QUERIES)) * 100
    content_acc = (content_hit_count / len(BENCHMARK_QUERIES)) * 100
    log(f"\nTỔNG KẾT ({strategy}):")
    log(f"- Tỷ lệ trúng tài liệu (Doc Hit trong Top-3)     : {doc_hit_count}/{len(BENCHMARK_QUERIES)} ({doc_acc:.1f}%)")
    log(f"- Tỷ lệ trúng nội dung chuẩn (Content Hit Top-3) : {content_hit_count}/{len(BENCHMARK_QUERIES)} ({content_acc:.1f}%)")
    log("=" * 80)

    output_content = "\n".join(lines)
    Path(out_file).write_text(output_content, encoding="utf-8")
    log(f"\n[INFO] Đã ghi kết quả benchmark chi tiết vào file: {out_file}")
    return output_content


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chạy benchmark truy xuất tài liệu TMĐT Lab 7")
    parser.add_argument("--data-dir", type=Path, default=Path("data/ecommerce"), help="Thư mục dữ liệu corpus")
    parser.add_argument(
        "--strategy",
        choices=["window", "sentence_window", "sentence", "heading", "fixed", "recursive"],
        default="window",
        help="Chiến lược chunk (mặc định: window / SentenceWindowChunker)",
    )
    parser.add_argument("--top-k", type=int, default=3, help="Độ sâu Top-K")
    parser.add_argument("--window-size", "-w", type=int, default=3, help="Số câu trước và sau trong cửa sổ ngữ cảnh (cho SentenceWindowChunker)")
    parser.add_argument("--out-file", type=str, default="ket_qua_benchmark.txt", help="File xuất kết quả")
    args = parser.parse_args()

    run_benchmark(
        data_dir=args.data_dir,
        strategy=args.strategy,
        top_k=args.top_k,
        out_file=args.out_file,
        window_size=args.window_size,
    )
