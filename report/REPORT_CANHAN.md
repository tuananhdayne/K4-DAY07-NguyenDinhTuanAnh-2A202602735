# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Đình Tuấn Anh  
**Nhóm:** Nhóm 2A — K4-L3B (Thương Mại Điện Tử)  
**Ngày:** 2026-09-20  

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao (tiến gần về 1.0) nghĩa là hai vector embedding cùng chỉ về một hướng trong không gian vector đa chiều. Về mặt ngữ nghĩa, điều này thể hiện hai đoạn văn bản có sự tương đồng nội dung rất cao, truyền tải cùng một ý nghĩa cốt lõi dù độ dài hay cách dùng từ có thể khác nhau.

**Ví dụ có độ tương tự CAO:**
- **Câu A:** Shopee hỗ trợ Người mua gửi yêu cầu Trả hàng và Hoàn tiền trong vòng 15 ngày kể từ khi nhận hàng.
- **Câu B:** Khách hàng có thời hạn 15 ngày để khiếu nại đổi trả sản phẩm hoặc yêu cầu hoàn lại tiền trên Shopee.
- **Tại sao tương đồng:** Cả hai câu đều nói về cùng một chính sách quy định (quyền lợi và mốc thời gian 15 ngày để đổi trả/hoàn tiền trên Shopee), sử dụng các từ đồng nghĩa ngữ cảnh ("Người mua" / "Khách hàng", "Trả hàng và Hoàn tiền" / "đổi trả sản phẩm hoặc yêu cầu hoàn lại tiền").

**Ví dụ có độ tương tự THẤP:**
- **Câu A:** Shopee hỗ trợ Người mua gửi yêu cầu Trả hàng và Hoàn tiền trong vòng 15 ngày kể từ khi nhận hàng.
- **Câu B:** Thời tiết hôm nay tại Hà Nội nhiều mây và có thể xuất hiện mưa rào rải rác vào chiều tối.
- **Tại sao khác:** Hai câu thuộc hai miền kiến thức hoàn toàn độc lập và không liên quan (chính sách sàn thương mại điện tử đối lập với bản tin dự báo khí tượng thời tiết), không chia sẻ bất kỳ trường từ vựng hay mối quan hệ ngữ nghĩa nào.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Khoảng cách Euclid đo khoảng cách hình học tuyệt đối giữa hai điểm, do đó bị ảnh hưởng nặng nề bởi độ dài vector (magnitude) — một đoạn văn dài nhiều từ lặp lại sẽ bị kéo xa một đoạn văn ngắn dù hai đoạn nói cùng một ý. Ngược lại, độ tương tự cosine chỉ đo góc lệch giữa hai vector (chuẩn hóa độ dài về 1), cho phép so sánh sự tương đồng về ngữ nghĩa thuần túy mà không bị thiên vị bởi độ dài văn bản.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*  
> Áp dụng công thức:  
> $$\text{số lượng chunk} = \lceil \frac{\text{độ\_dài\_tài\_liệu} - \text{độ\_chồng\_chéo}}{\text{kích\_thước\_chunk} - \text{độ\_chồng\_chéo}} \rceil$$  
> Bước nhảy (stride) giữa các chunk là: $500 - 50 = 450$ ký tự.  
> Chi tiết:  
> $$\frac{10,000 - 50}{500 - 50} = \frac{9,950}{450} \approx 22.111$$  
> Làm tròn lên: $\lceil 22.111 \rceil = 23$  
> (Phân bổ vị trí: Chunk 1: [0, 500], Chunk 2: [450, 950], ..., Chunk 22: [9450, 9950], Chunk 23: [9900, 10000]).  
> *Đáp án:* **23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap = 100, bước nhảy giảm còn $500 - 100 = 400$ ký tự.  
> Số lượng chunk mới: $\lceil \frac{10,000 - 100}{500 - 100} \rceil = \lceil \frac{9,900}{400} \rceil = \lceil 24.75 \rceil = 25$ chunks (tăng thêm 2 chunks).  
> Chúng ta muốn tăng độ chồng chéo để bảo vệ ngữ cảnh tại các điểm phân tách (boundaries), ngăn chặn nguy cơ câu văn, mệnh đề điều kiện hoặc tên thực thể quan trọng bị cắt đôi giữa hai chunk liên tiếp, giúp mô hình embedding nắm bắt thông tin trọn vẹn hơn.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Sử dụng regex Zero-width Positive Lookbehind: `r"(?<=[.!?])\s+"`. Kỹ thuật này giúp tách chuỗi ngay sau dấu ngắt câu (`.`, `!`, `?`) và theo sau bởi khoảng trắng mà không nuốt mất dấu câu (khắc phục hoàn toàn bẫy làm cụt câu của regex `[.!?]\s+`). Sau đó, thuật toán gom nhóm `max_sentences_per_chunk` câu liên tiếp thành một chunk và loại bỏ khoảng trắng thừa đầu cuối (`strip()`).  
> *Xử lý ngoại lệ & Edge cases:* Chuỗi rỗng hoặc chỉ có khoảng trắng trả về `[]` an toàn; loại bỏ các câu rỗng do nhiều dấu cách liên tiếp. Đã ghi nhận edge case chưa giải quyết triệt để: từ viết tắt (`TS.`, `ThS.`, `v.v.`) hoặc số thập phân (`1.5`, `10.000`) có thể bị ngắt sai vị trí do chứa dấu chấm.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Áp dụng thuật toán đệ quy chia để trị (divide & conquer) với danh sách dấu phân cách phân cấp từ lớn đến nhỏ: `["\n\n", "\n", ". ", " "]`.  
> *Base case:* Nếu độ dài văn bản $\le$ `chunk_size`, trả về nguyên văn bản mà không chia nhỏ tiếp; nếu đoạn văn vẫn vượt quá kích thước nhưng danh sách dấu phân cách đã cạn kiệt, thuật toán fallback cắt cứng chuỗi theo độ dài `chunk_size`.  
> *Quá trình đệ quy:* Tách văn bản bằng dấu phân cách hiện tại; nếu đoạn con vượt ngưỡng, gọi đệ quy `_split` với danh sách dấu phân cách còn lại. Cuối cùng, gom các đoạn con liên tiếp lại bằng dấu phân cách tương ứng sao cho tổng dung lượng không vượt quá `chunk_size`.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Lưu trữ tài liệu dưới dạng danh sách từ điển (`dict`) trong bộ nhớ trong (`self._store`). Khi gọi `add_documents`, mỗi `Document` được đưa qua `_embedding_fn` để trích xuất vector đặc trưng (chuẩn hóa L2-norm = 1.0), tự động gán hoặc bảo toàn metadata `doc_id` rồi lưu trữ.  
> Trong hàm `search`, vector truy vấn được nhân tích vô hướng (`_dot`) với từng vector tài liệu đã lưu (tương đương Cosine Similarity do các vector đều có độ dài bằng 1). Các bản ghi được sắp xếp giảm dần theo điểm số (`score`) và trả về `top_k` kết quả cao nhất.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Áp dụng chiến lược **Tiền lọc (Pre-filtering)** cho `search_with_filter`: Quét toàn bộ danh sách `self._store` và chỉ giữ lại các bản ghi thỏa mãn tất cả các điều kiện khóa-giá trị trong `metadata_filter` (`all(r["metadata"].get(k) == v for k, v in metadata_filter.items())`), sau đó mới tính điểm tương tự trên tập ứng viên này. Điều này đảm bảo độ chính xác 100% về đối tượng (`audience`) và tăng tốc độ tìm kiếm.  
> Đối với `delete_document`, sử dụng list comprehension để lọc bỏ toàn bộ các bản ghi có `metadata["doc_id"] == doc_id` hoặc `id == doc_id`. Trả về `True` nếu độ dài danh sách sau khi lọc giảm đi so với ban đầu, ngược lại trả về `False`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Xây dựng prompt theo mô hình RAG tiêu chuẩn gồm 3 cấu phần: (1) System Instructions yêu cầu trả lời trung thực, khách quan, chỉ dựa vào ngữ cảnh và đánh số trích dẫn nguồn `[1], [2]...`, từ chối trả lời nếu thiếu dữ liệu; (2) Khối `--- NGỮ CẢNH ---` chứa các đoạn văn bản trích xuất từ `EmbeddingStore` (có thể kèm `metadata_filter`); (3) Khối `--- CÂU HỎI ---` chứa truy vấn của người dùng.  
> Cách đưa ngữ cảnh: Duyệt qua từng kết quả từ `search` hoặc `search_with_filter`, định dạng mỗi đoạn thành `[{index}] (Nguồn: {source})\n{content}`, nối lại bằng `\n\n` rồi chèn trực tiếp vào prompt chuyển đến hàm `llm_fn`.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0 -- /home/tuananh/vinuni/209/K4-DAY07-NguyenDinhTuanAnh-2A202602735/.venv/bin/python3
cachedir: .pytest_cache
rootdir: /home/tuananh/vinuni/209/K4-DAY07-NguyenDinhTuanAnh-2A202602735
collecting ... collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================== 42 passed in 0.03s ==============================
```

**Số lượng bài test vượt qua (pass):** **42 / 42** (100%)

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Chạy hàm `compute_similarity()` với `MockEmbedder` trên 5 cặp câu:

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|:---:|-------|-------|:---:|:---:|:---:|
| 1 | Shopee hỗ trợ trả hàng và hoàn tiền trong vòng 15 ngày. | Người mua có 15 ngày để yêu cầu đổi trả hàng hoặc hoàn tiền. | Cao | -0.0708 | Không (Sai do Mock) |
| 2 | Thời gian xử lý khiếu nại của Shopee thường từ 3 đến 5 ngày làm việc. | Shopee xem xét bằng chứng và phản hồi khiếu nại trong 3-5 ngày. | Cao | +0.1240 | Đúng |
| 3 | Người mua cần chụp ảnh rõ nét nhãn bưu kiện và sản phẩm hư hỏng. | Cần gửi kèm video mở hộp và hình ảnh tem nhãn khi yêu cầu hoàn tiền. | Cao | +0.0903 | Đúng |
| 4 | Chính sách trả hàng và hoàn tiền dành cho Người mua trên sàn Shopee. | Trời hôm nay nắng ráo, nhiệt độ trung bình khoảng 28 độ C. | Thấp | +0.0624 | Đúng |
| 5 | Sản phẩm thực phẩm tươi sống chỉ được yêu cầu trả hàng trong vòng 24 giờ. | Thủ tục xin cấp giấy phép xây dựng nhà ở riêng lẻ tại cơ quan quận huyện. | Thấp | +0.1038 | Không (Sai do Mock) |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Kết quả bất ngờ nhất xuất hiện ở **Cặp 1**: hai câu có nội dung ngữ nghĩa đồng nhất (quy định 15 ngày đổi trả/hoàn tiền) nhưng điểm tương tự thực tế lại mang giá trị âm (-0.0708), trong khi Cặp 5 hoàn toàn không liên quan lại có điểm dương cao hơn (+0.1038).  
> Điều này phản ánh rõ ràng rằng `MockEmbedder` chỉ băm chuỗi ký tự bằng MD5 để sinh vector ngẫu nhiên nên hoàn toàn không thể hiểu được ngữ nghĩa thực sự (semantic meaning). Bất kỳ thay đổi nhỏ về từ vựng hay cấu trúc cú pháp đều khiến vector bị phân tán ngẫu nhiên. Để biểu diễn chính xác ý nghĩa và quan hệ giữa các câu trong hệ thống RAG thực tế, bắt buộc phải sử dụng các mô hình ngôn ngữ nhúng chuyên sâu (như Sentence Transformers đa ngôn ngữ hoặc OpenAI/Gemini Embeddings), nơi các khái niệm ngữ nghĩa tương đồng được ánh xạ gần nhau trong không gian vector liên tục.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src` (`SentenceChunker`, `max_sentences_per_chunk=3`). **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|:---:|:---:|------------------------|
| 1 | Thời gian tối đa để Người mua gửi yêu cầu Trả hàng/Hoàn tiền cho Shopee là bao lâu? | `cach-dong-goi-don-hang-hoan-tra#5`: Hướng dẫn viết mã vận đơn lên hộp hàng hoàn trả trên ứng dụng... | +0.2909 | **Không (Irrelevant)** | Dựa trên ngữ cảnh: Trả lời về cách ghi mã vận đơn lên hộp hàng (do MockEmbedder băm MD5 chưa bắt đúng ngữ nghĩa). |
| 2 | Những trường hợp hoặc mặt hàng nào không được chấp nhận trả hàng do đổi ý? | `quy-trinh-shopee-xu-ly-tra-hang-hoan-tien#10`: Hướng dẫn theo dõi tình trạng vận chuyển đơn hàng hoàn trả... | +0.3032 | **Không (Irrelevant)** | Dựa trên ngữ cảnh: Hướng dẫn theo dõi trạng thái bưu kiện hoàn trả. |
| 3 | Người mua có phải trả phí vận chuyển khi gửi hàng hoàn trả không? | `tra-hang-doi-y-khong-con-nhu-cau#3`: Quy định về hàng hóa có giá trị cao hoặc kích thước cồng kềnh... | +0.2812 | **Không (Irrelevant)** | Dựa trên ngữ cảnh: Đề cập đến sản phẩm cồng kềnh, chưa trả lời chính sách miễn phí hoàn trả. |
| 4 ⭐ | Thời hạn xử lý và phản hồi yêu cầu bảo hành hoặc khiếu nại của khách hàng là bao lâu? *(Filter: `audience="seller"`)* | `seller-warranty-policy#1`: Người bán phải tiếp nhận xử lý bảo hành trong tối đa 03 ngày làm việc; phản hồi khiếu nại từ 1 - 2 ngày làm việc... | -0.0177 | **CÓ (Relevant — Top-1 Hit)** | Dựa trên ngữ cảnh [1]: Người bán phải tiếp nhận và xử lý bảo hành trong tối đa 03 ngày làm việc; thời hạn phản hồi khiếu nại Trả hàng/Hoàn tiền là từ 1 - 2 ngày làm việc. |
| 5 | Thời gian nhận tiền hoàn qua SPayLater hoặc Thẻ tín dụng/ghi nợ mất bao lâu? | `quy-trinh-shopee-xu-ly-tra-hang-hoan-tien#1`: Hướng dẫn cung cấp bằng chứng cho yêu cầu Trả hàng/Hoàn tiền... | +0.2316 | **Không (Irrelevant)** | Dựa trên ngữ cảnh: Giải thích việc bổ sung bằng chứng khiếu nại. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **1 / 5** (với MockEmbedder; kết quả này hoàn toàn phù hợp với lưu ý trong `day7-lab-data-foundations.md` rằng MockEmbedder băm MD5 chuỗi ký tự nên không mã hóa ngữ nghĩa. Tuy nhiên, nhờ có bộ lọc siêu dữ liệu `audience="seller"`, câu 4 đã xuất sắc trúng Top-1 cả về Document lẫn Content).

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> 1. **Hiệu lực tuyệt đối của Metadata Filtering (Câu Q4):** Trong môi trường MockEmbedder hay kể cả embedding thực tế, khi câu hỏi không ghi rõ vai vế của người hỏi, bộ lọc siêu dữ liệu cứng (`audience: "seller"`) là cơ chế duy nhất đảm bảo khoanh vùng chính xác vào tài liệu `seller-warranty-policy.md`, ngăn chặn triệt để việc nhầm lẫn sang chính sách 15 ngày của Người mua.
> 2. **Header Injection của HeadingChunker:** Kỹ thuật chèn lại tiêu đề đề mục vào từng đoạn con của Thành viên 2 giúp các chunk nhỏ không bao giờ bị mất gốc ngữ cảnh (context loss) khi trích xuất vào LLM.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|:---:|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
