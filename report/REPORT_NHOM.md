# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Nhóm 2A — K4-L3B (Thương Mại Điện Tử)  
**Thành viên:** Nguyễn Đình Tuấn Anh (và các thành viên trong nhóm)  
**Ngày:** 2026-09-20  

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Chính sách Trả hàng và Hoàn tiền của Sàn Thương mại Điện tử Shopee (Shopee Return & Refund Policy — Biến thể K4-L3B).

**Tại sao nhóm chọn chủ đề này?**
> Chính sách đổi trả trên sàn TMĐT là một trong những bài toán phổ biến và thách thức nhất trong việc xây dựng hệ thống trợ lý CSKH tự động (Customer Support Agent). Tài liệu chứa nhiều quy tắc ràng buộc chặt chẽ, mốc thời gian pháp lý (24 giờ, 15 ngày, 3-5 ngày), điều kiện ngoại lệ và phân định trách nhiệm rõ ràng giữa Người mua và Người bán. Đây là miền dữ liệu lý tưởng để kiểm chứng năng lực của các kỹ thuật Chunking và lọc Siêu dữ liệu (Metadata Filtering).

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Cách đóng gói đơn hàng hoàn trả | https://help.shopee.vn/portal/4/article/79508 | 2026-09-20 / not-stated | 4,767 | `doc_id`, `title`, `audience: buyer`, `category: shipping-policy`, `language: vi` |
| 2 | Hướng dẫn chuẩn bị bằng chứng khi yêu cầu Trả hàng và Hoàn tiền | https://help.shopee.vn/portal/4/article/79467 | 2026-09-20 / not-stated | 3,958 | `doc_id`, `title`, `audience: buyer`, `category: return-process`, `language: vi` |
| 3 | Hướng dẫn gửi yêu cầu Trả hàng và Hoàn tiền | https://help.shopee.vn/portal/4/article/79233 | 2026-09-20 / not-stated | 2,712 | `doc_id`, `title`, `audience: buyer`, `category: return-process`, `language: vi` |
| 4 | Các phương thức gửi hàng hoàn trả và phí hoàn trả | https://help.shopee.vn/portal/4/article/189477 | 2026-09-20 / not-stated | 7,425 | `doc_id`, `title`, `audience: buyer`, `category: shipping-policy`, `language: vi` |
| 5 | Chính sách đổi trả và hoàn tiền của Shopee | https://help.shopee.vn/portal/4/article/188931 | 2026-09-20 / not-stated | 2,850 | `doc_id: return-refund-policy`, `title`, `audience: buyer`, `category: returns-policy`, `language: vi` |
| 6 | Quy định bảo hành và xử lý khiếu nại dành cho Người bán | https://banhang.shopee.vn/edu/article/190387 | 2026-09-20 / 2026.1 | 1,840 | `doc_id: seller-warranty-policy`, `title`, `audience: seller`, `category: seller-policy`, `language: vi` |
| 7 | Quy trình Shopee xử lý yêu cầu Trả hàng và Hoàn tiền | https://help.shopee.vn/portal/4/article/190242 | 2026-09-20 / not-stated | 8,769 | `doc_id`, `title`, `audience: both`, `category: dispute-resolution`, `language: vi` |
| 8 | Sản phẩm hạn chế trả hàng trên Shopee | https://help.shopee.vn/portal/4/article/79465 | 2026-09-20 / not-stated | 1,490 | `doc_id`, `title`, `audience: buyer`, `category: returns-policy`, `language: vi` |
| 9 | Thời gian nhận tiền hoàn và cách kiểm tra tiền hoàn trên Shopee | https://help.shopee.vn/portal/4/article/189473 | 2026-09-20 / not-stated | 6,144 | `doc_id`, `title`, `audience: buyer`, `category: refund-policy`, `language: vi` |
| 10 | Những điều cần biết về Trả hàng do Đổi ý hoặc không còn nhu cầu | https://help.shopee.vn/portal/4/article/204305 | 2026-09-20 / not-stated | 7,700 | `doc_id`, `title`, `audience: buyer`, `category: returns-policy`, `language: vi` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.
- [x] Đa dạng đối tượng `audience`: có 8 tài liệu `buyer`, 1 tài liệu `seller`, 1 tài liệu `both` (đảm bảo điều kiện cần ≥ 2 đối tượng).

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string | `quy-dinh-chung-tra-hang-hoan-tien` | Định danh tài liệu gốc theo chuẩn kebab-case, dùng để liên kết chunk với tài liệu và hỗ trợ hàm `delete_document()`. |
| `title` | string | `Những quy định chung về Trả hàng và Hoàn tiền của Shopee` | Cung cấp tiêu đề bài viết cho LLM trích dẫn nguồn hoặc tạo câu trả lời mạch lạc. |
| `audience` | string | `buyer`, `seller`, `both` | **Cốt lõi để tiền lọc (pre-filter):** Phân biệt câu hỏi của Người mua và Người bán khi câu hỏi không nêu rõ vai vế. |
| `category` | string | `returns-policy`, `refund-policy`, `shipping-policy` | Cho phép truy vấn khoanh vùng theo nghiệp vụ (ví dụ chỉ tìm trong chính sách vận chuyển hoặc tài chính). |
| `language` | string | `vi` | Phân loại ngôn ngữ hỗ trợ truy vấn đa ngôn ngữ sau này. |
| `source_url` | string | `https://help.shopee.vn/portal/4/article/188931` | Truy vết nguồn gốc chính thống để người dùng đối chiếu. |
| `retrieved_at` | string | `2026-09-20` | Kiểm soát tính cập nhật (freshness) của chính sách. |
| `document_version` | string | `not-stated` | Lưu trữ số hiệu phiên bản chính sách khi sàn cập nhật điều khoản mới. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu trong bộ dữ liệu (đã bóc tách frontmatter trước khi đo):

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình (ký tự) | Giữ được ngữ cảnh không? |
|-----------|----------|:---:|:---:|---|
| **1. Quy định chung về Trả hàng/Hoàn tiền** (`quy-dinh-chung-tra-hang-hoan-tien.md` - 6,707 ký tự) | FixedSizeChunker (`fixed_size`) | 27 | 296.6 | **Kém**: Cắt ngang các câu điều kiện và mốc thời gian (ví dụ bị cắt giữa chừng "15 ngày..." và "...kể từ lúc"). |
| | SentenceChunker (`by_sentences`) | 9 | 741.4 | **Tốt**: Giữ trọn vẹn ngữ nghĩa của từng câu điều kiện, không bị cụt câu. |
| | RecursiveChunker (`recursive`) | 31 | 214.7 | **Khá**: Tách theo đoạn `\n\n` rồi câu `. `, các khối văn bản ngắn gọn nhưng đôi khi phân mảnh. |
| **2. Thời gian nhận tiền hoàn** (`thoi-gian-va-cach-kiem-tra-tien-hoan.md` - 5,850 ký tự) | FixedSizeChunker (`fixed_size`) | 24 | 291.7 | **Kém**: Cắt đôi các dòng trong bảng tra cứu thời hạn hoàn tiền của các ngân hàng. |
| | SentenceChunker (`by_sentences`) | 3 | 1945.0 | **Kém**: Do tài liệu nhiều bảng và bullet list ít dấu chấm câu chuẩn, khiến câu bị dồn quá dài. |
| | RecursiveChunker (`recursive`) | 29 | 200.4 | **Tốt**: Bóc tách mượt mà theo các dòng xuống dòng `\n` của bảng biểu. |
| **3. Phương thức gửi hàng hoàn trả và phí** (`phuong-thuc-gui-hang-va-phi-hoan-tra.md` - 7,143 ký tự) | FixedSizeChunker (`fixed_size`) | 29 | 294.6 | **Trung bình**: Cắt rời bước thao tác và điều kiện miễn cước. |
| | SentenceChunker (`by_sentences`) | 10 | 711.6 | **Tốt**: Giữ nguyên vẹn hướng dẫn của từng phương thức gửi hàng. |
| | RecursiveChunker (`recursive`) | 31 | 228.5 | **Tốt**: Đảm bảo kích thước đồng đều và giữ cấu trúc các mục con. |

---

### Chiến lược của từng thành viên

**Thành viên 1 — Nguyễn Đình Tuấn Anh**
- **Loại chiến lược:** `SentenceChunker` (`by_sentences`) với `max_sentences_per_chunk=3`.
- **Mô tả & lý do chọn:** 
  Chính sách thương mại điện tử phụ thuộc chặt chẽ vào các câu điều kiện ("Nếu... thì...", "Trong vòng... ngày"). `SentenceChunker` bảo toàn tính trọn vẹn của từng câu mệnh đề, tránh hiện tượng câu cụt làm mất điều kiện ràng buộc. Áp dụng Positive Lookbehind `(?<=[.!?])\s+` để tránh bẫy nuốt mất dấu câu.
- **Code snippet:**
```python
class SentenceChunker:
    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
        chunks: list[str] = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            chunk = " ".join(sentences[i : i + self.max_sentences_per_chunk]).strip()
            if chunk:
                chunks.append(chunk)
        return chunks
```

**Thành viên 2 — [Thành viên 2]**
- **Loại chiến lược:** `HeadingChunker` (`heading`) tùy biến theo tiêu đề Markdown (`#`, `##`, `###`).
- **Mô tả & lý do chọn:** 
  Văn bản chính sách Shopee vốn đã được chia thành các đề mục lớn nhỏ rất khoa học. `HeadingChunker` tách theo từng mục nội dung; nếu mục nào vượt quá 500 ký tự sẽ hạ bậc xuống `RecursiveChunker` và tự động gắn lại tiêu đề mục vào đầu mỗi mảnh con để không bao giờ mất ngữ cảnh.
- **Code snippet:**
```python
class HeadingChunker:
    def __init__(self, max_chunk_size: int = 500) -> None:
        self.max_chunk_size = max_chunk_size
        self._recursive = RecursiveChunker(chunk_size=max_chunk_size)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        sections = [s.strip() for s in re.split(r"(?m)(?=^#{1,4}\s+)", text.strip()) if s.strip()]
        chunks = []
        for sec in sections:
            if len(sec) <= self.max_chunk_size:
                chunks.append(sec)
            else:
                lines = sec.split("\n", 1)
                heading = lines[0].strip() if lines[0].startswith("#") else ""
                body = lines[1].strip() if len(lines) > 1 else ""
                for sub in self._recursive.chunk(body):
                    chunks.append(f"{heading}\n\n{sub}" if (heading and not sub.startswith(heading)) else sub)
        return chunks
```

**Thành viên 3 — [Thành viên 3]**
- **Loại chiến lược:** `RecursiveChunker` (`recursive`) với các dấu phân cách ưu tiên `["\n\n", "\n", ". ", " ", ""]`, `chunk_size=300`.
- **Mô tả & lý do chọn:** 
  Tận dụng sự phân cấp tự nhiên của văn bản. Cắt ưu tiên theo ranh giới đoạn văn `\n\n`, sau đó đến dòng `\n`, rồi mới đến câu. Giúp kiểm soát trần kích thước chunk không vượt quá giới hạn ngữ cảnh của mô hình nhúng.

---

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|:---:|-----------|----------|
| Tuấn Anh | `SentenceChunker` | 8/10 | Giữ trọn vẹn ngữ nghĩa câu quy định, các mốc thời gian không bị ngắt quãng. | Kém hiệu quả với các bảng số liệu ngân hàng và danh sách gạch đầu dòng dài. |
| Thành viên 2 | `HeadingChunker` | 10/10 | Bảo toàn ngữ cảnh cấu trúc tài liệu hoàn hảo; các mảnh con luôn biết rõ thuộc điều khoản nào. | Cần văn bản nguồn có định dạng Markdown heading chuẩn mực. |
| Thành viên 3 | `RecursiveChunker` | 8/10 | Kích thước chunk đồng đều, xử lý linh hoạt mọi dạng định dạng từ bảng đến văn xuôi. | Có thể cắt rời một danh sách ngắn ra làm 2 phần nếu chạm ngưỡng kích thước. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> **`HeadingChunker` là chiến lược vượt trội nhất cho tài liệu chính sách/quy chế.** Các văn bản quy định của Shopee đều được chia theo các phần ngữ nghĩa độc lập thông qua tiêu đề mục (`1. Điều kiện...`, `2. Thời gian...`). Việc tách theo heading kết hợp gắn lại tiêu đề (header injection) vào từng mảnh con giúp mô hình nhúng nhận diện chính xác chủ đề ngay cả khi trích xuất một đoạn chi tiết nhỏ ở sâu bên dưới.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> Bộ 5 câu hỏi chuẩn hóa bao gồm đầy đủ các dạng câu hỏi thực tế: tra cứu số liệu, điều kiện ràng buộc, các bước quy trình và bảng danh sách phương thức.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | **Thời gian tối đa để Người mua gửi yêu cầu Trả hàng/Hoàn tiền cho Shopee là bao lâu?** | - Đơn hàng thông thường: 15 ngày kể từ lúc giao hàng thành công.<br>- Thực phẩm tươi sống/đông lạnh: 24 giờ kể từ khi giao thành công.<br>- Đơn Người bán tự vận chuyển: 15 ngày từ khi bấm nhận hàng hoặc 20 ngày từ khi lấy hàng thành công. | `return-refund-policy.md` (Mục 1.2: Thời gian tối đa) |
| 2 | **Những trường hợp hoặc mặt hàng nào không được chấp nhận trả hàng do đổi ý?** | Các sản phẩm thuộc danh mục Hạn chế trả hàng (đồ lót, thực phẩm tươi sống, thẻ nạp, voucher...), sản phẩm đã qua sử dụng, hoặc bao bì/tem niêm phong của nhà sản xuất không còn nguyên vẹn. | `tra-hang-doi-y-khong-con-nhu-cau.md` & `san-pham-han-che-tra-hang.md` |
| 3 | **Người mua có phải trả phí vận chuyển khi gửi hàng hoàn trả không?** | Người mua được miễn phí hoàn trả 100% nếu lựa chọn hình thức hoàn trả tích hợp trên ứng dụng Shopee (Lấy hàng tận nơi hoặc Gửi tại bưu cục do Shopee chỉ định). | `phuong-thuc-gui-hang-va-phi-hoan-tra.md` (Mục 1 & 2) |
| 4 ⭐ | **Thời hạn xử lý và phản hồi yêu cầu bảo hành hoặc khiếu nại của khách hàng là bao lâu?** *(Bắt buộc lọc: `audience="seller"`)* | Người bán phải tiếp nhận và xử lý yêu cầu bảo hành trong tối đa 03 ngày làm việc; thời hạn phản hồi khiếu nại Trả hàng/Hoàn tiền là từ 1 - 2 ngày làm việc. (Không có bộ lọc sẽ bị lẫn sang thời hạn 15 ngày của Người mua). | `seller-warranty-policy.md` (Mục 1 & 2) |
| 5 | **Thời gian nhận tiền hoàn qua SPayLater hoặc Thẻ tín dụng/ghi nợ mất bao lâu?** | - SPayLater: Thường trong vòng 24 giờ (hạn mức khả dụng được hoàn lại ngay).<br>- Thẻ tín dụng/ghi nợ: Từ 7 - 14 ngày làm việc tùy theo chu kỳ của ngân hàng phát hành thẻ. | `thoi-gian-va-cach-kiem-tra-tien-hoan.md` (Mục 1.2) |

---

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|:---:|---------|
| 1 | Thời gian tối đa Người mua gửi yêu cầu Trả hàng/Hoàn tiền | `HeadingChunker` / `SentenceChunker` | Có (Top-1) | Truy xuất chính xác Mục 1.2 trong `return-refund-policy.md`. |
| 2 | Các trường hợp/mặt hàng không được trả hàng do đổi ý | `HeadingChunker` | Có (Top-1) | Lấy đúng danh mục hạn chế và yêu cầu bao bì nguyên vẹn. |
| 3 | Phí vận chuyển hàng hoàn trả | `HeadingChunker` / `SentenceChunker` | Có (Top-1) | Bắt trọn quy định miễn phí 100% khi gửi qua bưu cục/lấy tận nơi. |
| 4 ⭐ | Thời hạn xử lý bảo hành và phản hồi khiếu nại (Seller) | `HeadingChunker` + Filter `audience: seller` | Có (Top-1) | **Bắt buộc lọc metadata:** Khóa chặt tài liệu `seller-warranty-policy.md`. |
| 5 | Thời gian nhận tiền hoàn qua SPayLater/Thẻ tín dụng | `RecursiveChunker` / `HeadingChunker` | Có (Top-1) | Trích xuất chuẩn xác Mục 1.2 bảng thời hạn từng kênh thanh toán. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> **Lọc bằng metadata đóng vai trò quyết định ở Câu hỏi 4 (⭐):** Câu hỏi hỏi về *"Thời hạn xử lý và phản hồi yêu cầu bảo hành hoặc khiếu nại của khách hàng là bao lâu?"*. Trong kho dữ liệu, cả tài liệu Người mua (`return-refund-policy.md`) và Người bán (`seller-warranty-policy.md`) đều chứa các từ khóa tương đồng ("thời hạn", "khiếu nại", "yêu cầu", "khách hàng"). Nếu không dùng `metadata_filter={"audience": "seller"}`, công cụ retrieval sẽ trả về các chunk của Người mua (thời hạn 15 ngày), khiến câu trả lời bị sai hoàn toàn đối tượng. Khi áp dụng bộ lọc `audience: "seller"`, hệ thống loại bỏ 100% tài liệu của Người mua và lấy chính xác tài liệu `seller-warranty-policy.md` (03 ngày bảo hành và 1 - 2 ngày khiếu nại). Bằng chứng đối chiếu A/B test trong `bench.py` đã chứng minh điều này rõ rệt.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
1. **Sức mạnh của Heading Chunking trong văn bản pháp lý/chính sách:** Việc tôn trọng cấu trúc đề mục sẵn có kết hợp kỹ thuật gắn lại tiêu đề (header injection) giúp giải quyết triệt để vấn đề mất ngữ cảnh khi cắt nhỏ văn bản.
2. **Vai trò không thể thay thế của Metadata Filter:** Embedding chỉ so sánh độ tương đồng ngữ nghĩa về mặt từ vựng, không thể tự phân biệt vai trò đối tượng nếu không có bộ lọc siêu dữ liệu cứng (`audience: buyer` vs `seller`).
3. **Bẫy Lookbehind Regex:** Việc bảo toàn dấu câu bằng `(?<=[.!?])\s+` là mấu chốt để tránh làm câu bị cụt nghĩa.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một kho tài liệu, nhưng chiến lược chia nhỏ (chunking) quyết định trực tiếp tới 80% độ chính xác của câu trả lời. Chiến lược FixedSize đơn giản cắt ngang ranh giới câu làm mất hẳn các con số điều kiện ràng buộc; trong khi Chunking theo ngữ nghĩa (Heading/Sentence) giúp LLM nhận được đúng đoạn thông tin cô đọng và trả lời chuẩn xác.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ chuẩn hóa các bảng biểu HTML phức tạp sang định dạng Markdown Table rõ ràng hơn trước khi nạp vào vector store, đồng thời bổ sung thêm các trường metadata chuyên sâu như `transaction_type` (thực phẩm tươi sống / hàng thông thường / hàng điện tử) để tăng cường độ chính xác cho bộ lọc.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|:---:|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
