from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from app.core.config import get_settings
from app.ingestion.loaders import ParsedDocument, parse_document


@dataclass(slots=True)
class TextChunk:
    text: str
    page_number: int | None
    position: int
    token_count: int
    metadata: dict


def checksum_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def estimate_tokens(text: str) -> int:
    return max(1, len(re.findall(r"\S+", text)))


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    words = re.findall(r"\S+", text)
    if not words:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = max(end - overlap, start + 1)
    return chunks


def parse_and_chunk(path: str, content_type: str) -> tuple[ParsedDocument, list[TextChunk]]:
    settings = get_settings()
    parsed = parse_document(path, content_type)
    chunks: list[TextChunk] = []

    for page in parsed.pages:
        for text in chunk_text(page.text, settings.chunk_size, settings.chunk_overlap):
            chunks.append(
                TextChunk(
                    text=text,
                    page_number=page.page_number,
                    position=len(chunks),
                    token_count=estimate_tokens(text),
                    metadata=page.metadata or {},
                )
            )
    return parsed, chunks
