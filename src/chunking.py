from __future__ import annotations

import math
import re

# Chia văn bản thành các đoạn cố định
class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """
# size 1 chuck 500 , overlap 50 
    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap
# trả về list các chuck 
    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        # nếu độ dài text nhỏ hơn hoặc bằng chunk_size thì trả về list chứa text
        if len(text) <= self.chunk_size:
            return [text]
        # bước nhảy 
        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            # quét hết thì dừng
            if start + self.chunk_size >= len(text):
                break
        return chunks

# số đoạn văn tối đa trong 1 chuck 3 đoạn văn
class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
        if not sentences:
            return []
        chunks: list[str] = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            chunk = " ".join(sentences[i : i + self.max_sentences_per_chunk]).strip()
            if chunk:
                chunks.append(chunk)
        return chunks


class SentenceWindowChunker:
    """
    Sentence-Window Chunker:
    Splits text into individual sentences. For each sentence, constructs
    a sliding context window of `window_size` sentences before and after it.
    This ensures that every target sentence maintains its immediate surrounding
    context, avoiding context loss at arbitrary boundary cuts.
    """

    def __init__(self, window_size: int = 1) -> None:
        self.window_size = max(1, window_size)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
        if not sentences:
            return []
        if len(sentences) <= self.window_size * 2 + 1:
            return [" ".join(sentences)]

        chunks: list[str] = []
        seen: set[str] = set()
        for i in range(len(sentences)):
            start = max(0, i - self.window_size)
            end = min(len(sentences), i + self.window_size + 1)
            window_chunk = " ".join(sentences[start:end]).strip()
            if window_chunk and window_chunk not in seen:
                chunks.append(window_chunk)
                seen.add(window_chunk)
        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if not current_text:
            return []
        if len(current_text) <= self.chunk_size:
            return [current_text]
        if not remaining_separators:
            return [
                current_text[i : i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ]

        sep = remaining_separators[0]
        next_seps = remaining_separators[1:]

        if sep == "":
            return [
                current_text[i : i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ]

        if sep not in current_text:
            return self._split(current_text, next_seps)

        parts = current_text.split(sep)
        splits: list[str] = []
        for part in parts:
            if not part:
                continue
            if len(part) <= self.chunk_size:
                splits.append(part)
            else:
                splits.extend(self._split(part, next_seps))

        chunks: list[str] = []
        current_chunk: list[str] = []
        current_len = 0
        sep_len = len(sep)

        for piece in splits:
            piece_len = len(piece)
            if piece_len > self.chunk_size:
                if current_chunk:
                    chunks.append(sep.join(current_chunk))
                    current_chunk = []
                    current_len = 0
                chunks.append(piece)
                continue

            if current_chunk:
                if current_len + sep_len + piece_len <= self.chunk_size:
                    current_chunk.append(piece)
                    current_len += sep_len + piece_len
                else:
                    chunks.append(sep.join(current_chunk))
                    current_chunk = [piece]
                    current_len = piece_len
            else:
                current_chunk = [piece]
                current_len = piece_len

        if current_chunk:
            chunks.append(sep.join(current_chunk))

        return chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    norm_a = math.sqrt(sum(x * x for x in vec_a))
    norm_b = math.sqrt(sum(y * y for y in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return _dot(vec_a, vec_b) / (norm_a * norm_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        fixed_chunker = FixedSizeChunker(chunk_size=chunk_size)
        sentence_chunker = SentenceChunker()
        recursive_chunker = RecursiveChunker(chunk_size=chunk_size)

        strategies = {
            "fixed_size": fixed_chunker.chunk(text),
            "by_sentences": sentence_chunker.chunk(text),
            "recursive": recursive_chunker.chunk(text),
        }

        results: dict[str, dict] = {}
        for name, chunks in strategies.items():
            count = len(chunks)
            avg_length = sum(len(c) for c in chunks) / count if count > 0 else 0.0
            results[name] = {
                "count": count,
                "avg_length": avg_length,
                "chunks": chunks,
            }
        return results


class HeadingChunker:
    """
    Split Markdown text by headings (#, ##, ###, ####).
    Each heading section is treated as an independent semantic unit.
    Sections longer than max_chunk_size are recursively subdivided,
    with the section heading prepended to each sub-chunk to maintain context.
    """

    def __init__(self, max_chunk_size: int = 500) -> None:
        self.max_chunk_size = max_chunk_size
        self._recursive = RecursiveChunker(chunk_size=max_chunk_size)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        sections = [
            s.strip()
            for s in re.split(r"(?m)(?=^#{1,4}\s+)", text.strip())
            if s.strip()
        ]
        if not sections:
            return []

        chunks: list[str] = []
        for sec in sections:
            if len(sec) <= self.max_chunk_size:
                chunks.append(sec)
            else:
                lines = sec.split("\n", 1)
                heading = lines[0].strip() if lines[0].startswith("#") else ""
                body = lines[1].strip() if len(lines) > 1 else ""

                if not body:
                    chunks.append(sec[: self.max_chunk_size])
                    continue

                sub_chunks = self._recursive.chunk(body)
                for sub in sub_chunks:
                    if heading and not sub.startswith(heading):
                        chunks.append(f"{heading}\n\n{sub}")
                    else:
                        chunks.append(sub)

        return chunks
