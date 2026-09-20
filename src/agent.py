from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3, metadata_filter: dict | None = None) -> str:
        if self.store.get_collection_size() == 0:
            return "Không tìm thấy tài liệu trong cơ sở tri thức (kho lưu trữ trống)."

        if metadata_filter:
            results = self.store.search_with_filter(question, top_k=top_k, metadata_filter=metadata_filter)
        else:
            results = self.store.search(question, top_k=top_k)

        if not results:
            return "Không tìm thấy đoạn thông tin liên quan để trả lời câu hỏi."

        context_parts = []
        for index, item in enumerate(results, start=1):
            source = item.get("metadata", {}).get("source", item.get("id", f"doc_{index}"))
            context_parts.append(f"[{index}] (Nguồn: {source})\n{item['content']}")

        context_text = "\n\n".join(context_parts)

        prompt = (
            "Dựa trên ngữ cảnh được cung cấp dưới đây, hãy trả lời câu hỏi một cách trung thực và chính xác.\n"
            "Hãy trích dẫn rõ nguồn tương ứng với từng thông tin bằng ký hiệu [1], [2]...\n"
            "Chỉ dựa vào ngữ cảnh đã cho, không tự suy đoán thông tin ngoài ngữ cảnh. "
            "Nếu thông tin không đủ để trả lời, hãy thông báo rằng không tìm thấy thông tin.\n\n"
            f"--- NGỮ CẢNH ---\n{context_text}\n\n"
            f"--- CÂU HỎI ---\n{question}\n\n"
            "--- CÂU TRẢ LỜI ---"
        )

        return self.llm_fn(prompt)
