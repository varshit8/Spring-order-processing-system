import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from app.schemas import Citation

CHUNK_WORD_SIZE = 90
CHUNK_OVERLAP = 18
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "what",
    "with",
}


@dataclass
class StoredChunk:
    chunk_id: str
    document_id: str
    filename: str
    text: str
    tokens: set[str]


@dataclass
class StoredDocument:
    document_id: str
    filename: str
    source_type: str
    content: str
    created_at_utc: str
    chunk_ids: list[str]


class LocalRagStore:
    def __init__(self) -> None:
        self.documents: dict[str, StoredDocument] = {}
        self.chunks: dict[str, StoredChunk] = {}

    def clear(self) -> None:
        self.documents.clear()
        self.chunks.clear()

    def ingest(self, filename: str, content: str, source_type: str = "text") -> StoredDocument:
        normalized_content = normalize_whitespace(content)
        document_id = stable_id(f"{filename}:{normalized_content}")
        chunks = chunk_text(normalized_content)
        chunk_ids = []

        for index, chunk in enumerate(chunks, start=1):
            chunk_id = f"{document_id}-chunk-{index}"
            self.chunks[chunk_id] = StoredChunk(
                chunk_id=chunk_id,
                document_id=document_id,
                filename=filename,
                text=chunk,
                tokens=tokenize(chunk),
            )
            chunk_ids.append(chunk_id)

        document = StoredDocument(
            document_id=document_id,
            filename=filename,
            source_type=source_type,
            content=normalized_content,
            created_at_utc=datetime.now(timezone.utc).isoformat(),
            chunk_ids=chunk_ids,
        )
        self.documents[document_id] = document
        return document

    def list_documents(self) -> list[StoredDocument]:
        return sorted(self.documents.values(), key=lambda document: document.created_at_utc)

    def get_document(self, document_id: str) -> Optional[StoredDocument]:
        return self.documents.get(document_id)

    def search(self, query: str, top_k: int = 3, document_id: Optional[str] = None) -> list[Citation]:
        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        scored_chunks = []
        for chunk in self.chunks.values():
            if document_id and chunk.document_id != document_id:
                continue

            overlap = query_tokens.intersection(chunk.tokens)
            if not overlap:
                continue

            score = len(overlap) / max(len(query_tokens), 1)
            if any(token in chunk.text.lower() for token in query_tokens):
                score += 0.15
            scored_chunks.append((score, chunk))

        scored_chunks.sort(key=lambda item: item[0], reverse=True)
        return [
            Citation(
                document_id=chunk.document_id,
                filename=chunk.filename,
                chunk_id=chunk.chunk_id,
                excerpt=shorten(chunk.text),
                score=round(score, 4),
            )
            for score, chunk in scored_chunks[:top_k]
        ]


def stable_id(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def tokenize(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-zA-Z][a-zA-Z0-9_-]+", value.lower())
        if token not in STOPWORDS and len(token) > 2
    }


def chunk_text(content: str) -> list[str]:
    words = content.split()
    if len(words) <= CHUNK_WORD_SIZE:
        return [content]

    chunks = []
    step = CHUNK_WORD_SIZE - CHUNK_OVERLAP
    for start in range(0, len(words), step):
        section = words[start:start + CHUNK_WORD_SIZE]
        if section:
            chunks.append(" ".join(section))
    return chunks


def shorten(text: str, max_length: int = 280) -> str:
    if len(text) <= max_length:
        return text
    return text[: max_length - 3].rstrip() + "..."


def build_grounded_answer(question: str, citations: list[Citation]) -> str:
    if not citations:
        return (
            "I could not find enough indexed document context to answer that question. "
            "Upload a relevant document or ask about content that has already been indexed."
        )

    source_lines = [
        f"- {citation.excerpt}"
        for citation in citations
    ]
    return (
        f"Based on the indexed documents, the answer to '{question}' is grounded in these relevant passages:\n"
        + "\n".join(source_lines)
        + "\n\nReview the citations before using this in a final decision."
    )


def summarize_document(document: StoredDocument) -> str:
    sentences = split_sentences(document.content)
    selected = sentences[:4] if sentences else [shorten(document.content, 500)]
    return " ".join(selected)


def extract_action_items(document: StoredDocument) -> str:
    sentences = split_sentences(document.content)
    action_markers = (
        "must",
        "should",
        "need",
        "needs",
        "required",
        "action",
        "owner",
        "todo",
        "follow up",
    )
    actions = [
        sentence
        for sentence in sentences
        if any(marker in sentence.lower() for marker in action_markers)
    ]
    if not actions:
        return "No explicit action items were detected in this document."
    return "\n".join(f"- {action}" for action in actions[:8])


def split_sentences(content: str) -> list[str]:
    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", content)
        if sentence.strip()
    ]


rag_store = LocalRagStore()
