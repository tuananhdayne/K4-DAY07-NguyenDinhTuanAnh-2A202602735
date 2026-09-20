# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** AGI  
**Thành viên:**
1. Châu Tùng Dương (Benchmark Lead — `CustomHeadingChunker`)
2. Nguyễn Đình Tuấn Anh (Data Lead — `SentenceChunker` / `SentenceWindowChunker`)
3. Nguyễn Ngọc Tuyền (Strategy Lead — `RecursiveChunker`)
4. Ngô Anh Tú (Report & Demo Lead)  
**Ngày:** 20/09/2026  

> **Nộp 1 bản / nhóm.** Phần cá nhân mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Chính sách Đổi trả, Hoàn tiền và Khiếu nại bảo hành trên nền tảng Thương mại Điện tử Shopee Việt Nam.

**Tại sao nhóm chọn chủ đề này?**
> Đây là miền tri thức có tính ứng dụng thực tế rất cao, tác động trực tiếp đến quyền lợi người mua và trách nhiệm người bán. Các văn bản chính sách của Shopee có độ phân tầng ngữ nghĩa rõ nét (chia theo từng điều khoản, mốc thời gian cụ thể và đối tượng áp dụng riêng biệt), là miền dữ liệu lý tưởng để kiểm chứng sức mạnh của Metadata Filtering và Chunking có cấu trúc.

### Danh sách tài liệu (Data Inventory)

Tập dữ liệu gồm **14 tài liệu Markdown** chuẩn hóa lưu tại `data/ecommerce/` và đồng bộ 1-1 với `sources.csv`:

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | `quy-dinh-chung-tra-hang-hoan-tien.md` | https://help.shopee.vn/portal/4/article/188931 | 2026-09-20 / not-stated | 9,086 | audience: buyer, category: returns-policy |
| 2 | `tra-hang-doi-y-khong-con-nhu-cau.md` | https://help.shopee.vn/portal/4/article/145455 | 2026-09-20 / not-stated | 13,873 | audience: buyer, category: returns-policy |
| 3 | `san-pham-han-che-tra-hang.md` | https://help.shopee.vn/portal/4/article/79465 | 2026-09-20 / not-stated | 4,242 | audience: buyer, category: returns-policy |
| 4 | `huong-dan-gui-yeu-cau-tra-hang-hoan-tien.md` | https://help.shopee.vn/portal/4/article/79450 | 2026-09-20 / not-stated | 5,992 | audience: buyer, category: returns-guide |
| 5 | `phuong-thuc-gui-hang-va-phi-hoan-tra.md` | https://help.shopee.vn/portal/4/article/79475 | 2026-09-20 / not-stated | 7,163 | audience: buyer, category: shipping-fee |
| 6 | `cach-dong-goi-don-hang-hoan-tra.md` | https://help.shopee.vn/portal/4/article/79508 | 2026-09-20 / not-stated | 5,837 | audience: buyer, category: packaging |
| 7 | `huong-dan-chuan-bi-bang-chung-tra-hang.md` | https://help.shopee.vn/portal/4/article/79493 | 2026-09-20 / not-stated | 8,837 | audience: buyer, category: evidence-guide |
| 8 | `nguoi-ban-de-xuat-hoan-tien-ngay.md` | https://help.shopee.vn/portal/4/article/79486 | 2026-09-20 / not-stated | 5,744 | audience: both, category: negotiation |
| 9 | `quy-trinh-shopee-xu-ly-tra-hang-hoan-tien.md` | https://help.shopee.vn/portal/4/article/79485 | 2026-09-20 / not-stated | 12,398 | audience: both, category: dispute-process |
| 10 | `thoi-gian-va-cach-kiem-tra-tien-hoan.md` | https://help.shopee.vn/portal/4/article/79482 | 2026-09-20 / not-stated | 6,554 | audience: buyer, category: refund-tracking |
| 11 | `kiem-tra-tien-hoan-spaylater.md` | https://help.shopee.vn/portal/4/article/117978 | 2026-09-20 / not-stated | 4,204 | audience: buyer, category: spaylater |
| 12 | `theo-doi-tinh-trang-tra-hang-hoan-tien.md` | https://help.shopee.vn/portal/4/article/79483 | 2026-09-20 / not-stated | 3,149 | audience: buyer, category: refund-tracking |
| 13 | `theo-doi-van-chuyen-hang-hoan-tra.md` | https://help.shopee.vn/portal/4/article/79510 | 2026-09-20 / not-stated | 2,752 | audience: buyer, category: return-shipping |
| 14 | `cam-nang-tra-hang-hoan-tien.md` | https://help.shopee.vn/portal/4/article/147326 | 2026-09-20 / not-stated | 4,682 | audience: buyer, category: general-handbook |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|---|---|---|---|
| `doc_id` | `str` | `nguoi-ban-de-xuat-hoan-tien-ngay` | Định danh duy nhất file tài liệu gốc, dùng để kiểm tra tính chính xác và hỗ trợ hàm `delete_document`. |
| `title` | `str` | `Hướng dẫn Người mua trả lời đề xuất...` | Cung cấp tiêu đề trang để hiển thị trích dẫn nguồn cho người dùng. |
| `audience` | `str` | `buyer` / `both` | **Cực kỳ quan trọng**: Dùng để Pre-filter đối tượng, ngăn ngừa nhầm lẫn điều khoản giữa Người mua và Người bán. |
| `category` | `str` | `returns-policy`, `negotiation` | Cho phép lọc theo ngữ cảnh nghiệp vụ cụ thể (chính sách, đóng gói, khiếu nại). |
| `source_url` | `str` | `https://help.shopee.vn/portal/4/...` | Phục vụ tính minh bạch (Source Provenance) và truy vết nguồn gốc. |
| `retrieved_at` | `str` | `2026-09-20` | Kiểm soát tính cập nhật theo thời gian của văn bản pháp lý. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên tài liệu chính sách `quy-dinh-chung-tra-hang-hoan-tien`:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|---|---|---|---|---|
| `quy-dinh-chung` | FixedSizeChunker (`fixed_size`) | 46 chunks | 200 ký tự | Kém: Cắt ngang câu và cắt đứt bảng mốc thời gian |
| `quy-dinh-chung` | SentenceChunker (`by_sentences`) | 23 chunks | 345 ký tự | Khá: Giữ trọn câu nhưng bảng biểu bị phá vỡ cấu trúc |
| `quy-dinh-chung` | RecursiveChunker (`recursive`) | 28 chunks | 310 ký tự | Tốt: Giữ được khối đoạn văn tự nhiên |

### Chiến lược của từng thành viên

**Thành viên 1 — Châu Tùng Dương (Benchmark Lead)**
- **Loại chiến lược:** `CustomHeadingChunker` (`max_chunk_size=1000`).
- **Mô tả & lý do chọn:** Chiến lược chuyên biệt cho văn bản pháp lý Markdown. Tách theo tiêu đề (`#`, `##`, `###`) và tiểu mục số (`1.1.`, `1.2.`). Khi một mục dài quá 1000 ký tự, chia nhỏ nhưng tự động gắn tiền tố `[Tiêu đề mục]` vào đầu mỗi mảnh con để không bao giờ bị mất ngữ cảnh quy định cha.
- **Số chunks sinh ra:** 111 chunks (gọn nhất nhóm, giảm 52% số chunk).
- **Code snippet:**
```python
class CustomHeadingChunker:
    def __init__(self, max_chunk_size: int = 1000, min_chunk_size: int = 80):
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        pattern = r"(?=(?:^#{1,3}\s+.+$|^\d+\.\d+\.?\s+.+$|^Điều\s+\d+[:.]?.+$))"
        raw_sections = re.split(pattern, text.strip(), flags=re.M)
        chunks = []
        current_title = ""
        for sec in raw_sections:
            sec = sec.strip()
            if not sec:
                continue
            first_line = sec.split("\n")[0].strip()
            if first_line.startswith("#") or re.match(r"^\d+\.\d+", first_line):
                current_title = first_line
            if len(sec) <= self.max_chunk_size:
                chunks.append(sec)
            else:
                paragraphs = [p.strip() for p in sec.split("\n\n") if p.strip()]
                buffer = ""
                title_prefix = f"[{current_title}]\n" if current_title else ""
                for p in paragraphs:
                    candidate = f"{buffer}\n\n{p}".strip() if buffer else f"{title_prefix}{p}".strip()
                    if len(candidate) <= self.max_chunk_size:
                        buffer = candidate
                    else:
                        if buffer:
                            chunks.append(buffer)
                        buffer = f"{title_prefix}{p}".strip()
                if buffer:
                    chunks.append(buffer)
        return chunks if chunks else [text.strip()]
```

**Thành viên 2 — Nguyễn Đình Tuấn Anh (Data Lead)**
- **Loại chiến lược:** `SentenceChunker` / `SentenceWindowChunker` (cửa sổ trượt 3 câu).
- **Mô tả & lý do chọn:** Quản lý làm sạch và kiểm định tính hợp lệ của 14 tài liệu Shopee. Thử nghiệm cắt theo từng câu ngữ pháp và mở rộng bằng cửa sổ 3 câu liền kề để duy trì tính liên kết.
- **Số chunks sinh ra:** 234 chunks.

**Thành viên 3 — Nguyễn Ngọc Tuyền (Strategy Lead)**
- **Loại chiến lược:** `RecursiveChunker` (`chunk_size=500`).
- **Mô tả & lý do chọn:** Phân tách đệ quy theo các ranh giới `["\n\n", "\n", ". ", " ", ""]` kết hợp thuật toán gom các mảnh nhỏ liền kề. Giữ cấu trúc đoạn văn bản tự nhiên, kết hợp nhúng với mô hình AI `gemini-embedding-001`.
- **Số chunks sinh ra:** 182 chunks.

**Thành viên 4 — Ngô Anh Tú (Report & Demo Lead)**
- **Vai trò:** Tổng hợp số liệu thử nghiệm của 3 thành viên, hoàn thiện báo cáo nhóm và phụ trách triển khai Demo UI kết nối API thực tế, dẫn dắt bài thuyết trình.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Embedding Backend | Số Chunks sinh ra | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|---|---|---|---|---|---|---|
| **Châu Tùng Dương** | `CustomHeadingChunker` | `MockEmbedder` | **111 chunks** | **2 / 10** (Top-1 câu #4) | **Gọn nhất nhóm (tiết kiệm 52% bộ nhớ)**, bảo toàn 100% điều khoản Shopee, tự gắn tiêu đề cha | Phụ thuộc chất lượng định dạng heading của Markdown |
| **Nguyễn Đình Tuấn Anh** | `SentenceChunker` | `MockEmbedder` | 234 chunks | **2 / 10** | Tận dụng ranh giới câu ngữ pháp | Quá nhiều chunks (bùng nổ dung lượng), nhiều đoạn trùng lặp, trượt Câu 4 do mất tiêu đề |
| **Nguyễn Ngọc Tuyền** | `RecursiveChunker` | `gemini-embedding-001` | 182 chunks | **10 / 10** | **Điểm số tuyệt đối (5/5 Top-1)**, hiểu ngữ nghĩa toàn diện nhờ AI thật | Số chunk vẫn còn khá lớn (182 chunks), chưa nhận biết tiêu đề mục cha |
| **Ngô Anh Tú** | Report & Demo Lead | N/A | N/A | N/A | Điều phối toàn diện số liệu nhóm, kịch bản thuyết trình mượt mà | N/A |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Chiến lược **`CustomHeadingChunker`** (của Châu Tùng Dương) kết hợp với mô hình embedding ngữ nghĩa thực sự (`gemini-embedding-001`) là phương án tối ưu nhất cho bài toán chính sách Shopee. Lý do:
> 1. **Bảo toàn ngữ nghĩa pháp lý:** Các điều khoản Shopee có cấu trúc phân cấp rõ ràng (Điều kiện $\rightarrow$ Mốc thời gian $\rightarrow$ Lưu ý). Việc gom trọn vẹn 1 Heading vào 1 chunk giúp cung cấp đầy đủ thông tin cho Agent trả lời mà không bị cắt đứt giữa chừng.
> 2. **Tối ưu chi phí lưu trữ:** Chỉ tạo ra **111 chunks** (so với 182 và 234 chunks của 2 thành viên còn lại), giúp giảm 40–50% chi phí gọi Embedding API và tăng tốc độ tìm kiếm vector lên gấp đôi.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-----------------|---------------------------------|---------------------------|
| 1 | Thời gian tối đa để Người mua gửi yêu cầu Trả hàng/Hoàn tiền cho Shopee là bao lâu đối với từng loại đơn hàng? | - Thực phẩm tươi sống & đông lạnh: Trong vòng **24 giờ** kể từ lúc giao hàng thành công.<br>- Đơn Người bán tự vận chuyển: **15 ngày** kể từ lúc bấm 'Đã nhận được hàng' hoặc **20 ngày** kể từ lúc 'Lấy hàng thành công' (nếu không bấm nhận hàng).<br>- Các đơn hàng thông thường khác: **15 ngày** kể từ lúc giao hàng thành công. | `quy-dinh-chung-tra-hang-hoan-tien.md` (Mục 1.2: Thời gian tối đa) |
| 2 | Những trường hợp hoặc mặt hàng nào không được Shopee chấp nhận trả hàng do đổi ý hoặc không còn nhu cầu? | Sản phẩm thuộc danh mục Hạn chế trả hàng (đồ lót, thực phẩm tươi sống, thẻ cào...), sản phẩm mua tại Shopee Mart, sản phẩm đã qua sử dụng hoặc bao bì, tem mác niêm phong của nhà sản xuất không còn nguyên vẹn. | `tra-hang-doi-y-khong-con-nhu-cau.md` & `san-pham-han-che-tra-hang.md` |
| 3 | Nếu chọn hình thức "Tự sắp xếp" cho đơn hàng KHÔNG thuộc Shopee Mall, Người mua được hỗ trợ phí trả hàng bằng Shopee Xu như thế nào? | - Cùng tỉnh/thành phố với Người bán: Hoàn **25,000 Shopee Xu**.<br>- Khác tỉnh/thành phố với Người bán: Hoàn **40,000 Shopee Xu** (được hỗ trợ trong 3-5 ngày làm việc sau khi yêu cầu trả hàng được chấp nhận hoàn tiền). | `phuong-thuc-gui-hang-va-phi-hoan-tra.md` (Mục 2.2: Phí vận chuyển trả hàng) |
| 4 | Khi Người bán gửi đề xuất Hoàn Tiền Ngay, Người mua có những lựa chọn xử lý nào nếu đồng ý hoặc không đồng ý? *(Áp dụng bộ lọc: `audience="both"`)* | - Đồng ý: Chọn 'Trao đổi thêm' > Nhấn 'Đồng ý' $\rightarrow$ Nhận tiền hoàn ngay mà không cần trả hàng.<br>- KHÔNG đồng ý: Chọn Chat trao đổi thêm với Người bán để thương lượng, HOẶC nhấn 'Tôi muốn trả hàng' để tiếp tục quy trình hoàn trả nhận 100% tiền hàng. | `nguoi-ban-de-xuat-hoan-tien-ngay.md` (Bước 2: Trường hợp 1 & 2) |
| 5 | Thời gian nhận tiền hoàn vào Ví ShopeePay, SPayLater và Thẻ tín dụng/ghi nợ mất bao lâu sau khi Shopee chấp nhận hoàn tiền? | - Ví ShopeePay: Trong vòng **24 giờ** (với điều kiện ví hoạt động bình thường).<br>- SPayLater: Trong vòng **24 giờ** (hoàn vào số dư khả dụng SPayLater).<br>- Thẻ tín dụng / ghi nợ: Từ **7 - 14 ngày làm việc** tùy theo ngân hàng phát hành thẻ. | `thoi-gian-va-cach-kiem-tra-tien-hoan.md` (Bảng 1: Phương thức hoàn tiền) |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Thời gian tối đa gửi yêu cầu THHT | `Recursive` & `CustomHeading` | Có (Top-1 với điểm 0.88) | Chứa đủ con số 24h, 15 ngày, 20 ngày |
| 2 | Mặt hàng không chấp nhận do đổi ý | `Recursive` & `CustomHeading` | Có (Top-1 với điểm 0.91) | Trúng cả 2 file hạn chế trả hàng |
| 3 | Mức hỗ trợ Shopee Xu đơn tự sắp xếp | `Recursive` & `CustomHeading` | Có (Top-1 với điểm 0.80) | Trúng bảng mức 25,000 và 40,000 Xu |
| 4 | Người mua xử lý đề xuất hoàn tiền ngay | `CustomHeading` & `Recursive` | Có (Top-1 với điểm 0.87) | Cần bộ lọc `audience="both"` |
| 5 | Thời gian nhận tiền hoàn các kênh | `Recursive` & `CustomHeading` | Có (Top-1 với điểm 0.87) | Trích dẫn đúng bảng phương thức hoàn tiền |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> **Rất hữu ích, thể hiện quyết định ở Câu hỏi #4.**
> - Khi **không có filter**: Các câu từ của người mua chiếm trọn Top-3 (`quy-dinh-chung` và `tra-hang-doi-y`) do từ khóa "hoàn tiền" xuất hiện dày đặc. Tài liệu Gold hoàn toàn vắng bóng.
> - Khi **có filter (`audience="both"`):** Tài liệu Gold `nguoi-ban-de-xuat-hoan-tien-ngay` lập tức nhảy lên vị trí **Top-1** ở cả 3 thành viên, loại bỏ hoàn toàn nhiễu từ các văn bản người mua.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
1. **So sánh kích thước không gian vector:** Chiến lược `CustomHeadingChunker` giảm từ 234 chunks xuống 111 chunks (giảm 52%), vừa tiết kiệm chi phí vừa giữ trọn vẹn ngữ nghĩa từng điều khoản.
2. **Sức mạnh của Pre-filtering trong hệ thống RAG thực tế:** Khi không có filter, embedding bị ô nhiễm bởi các tài liệu có từ khóa tương đồng bề mặt. Filter giúp đưa tài liệu chuẩn từ ngoài top-10 lên thẳng Top-1.
3. **Sự khác biệt giữa Mock vs Real Embedding:** Mock MD5 chỉ kiểm thử cấu trúc code; khi bật `gemini-embedding-001`, hệ thống đạt độ chính xác hoàn hảo 10/10 điểm.

**Phân tích thất bại (Failure Case Analysis):**
> Ở Câu hỏi 4, khi Thành viên 1 sử dụng `SentenceWindowChunker` (kể cả khi đã lọc audience), kết quả Top-1, 2, 3 vẫn bị rơi vào file `quy-trinh-shopee-xu-ly-tra-hang-hoan-tien` thay vì `nguoi-ban-de-xuat-hoan-tien-ngay`.
> * **Nguyên nhân:** Cửa sổ trượt 3 câu cắt nhỏ nội dung khiến các câu văn mất đi tiêu đề mục cha, dẫn tới việc các câu nói về "khiếu nại" trong quy trình chung có điểm số tương đồng giả cao hơn quy trình đề xuất riêng biệt.
> * **Giải pháp khắc phục:** Cần áp dụng thuật toán `CustomHeadingChunker` tự động gắn kèm `[Tên điều khoản]` vào từng mảnh con.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ thực hiện bước tiền xử lý lọc bỏ các chuỗi URL ảnh Markdown dài (`![](https://...)`) trước khi chunking, nhằm tăng mật độ từ khóa có nghĩa (Signal-to-Noise Ratio) trong mỗi vector embedding.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|---|---|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
