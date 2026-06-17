from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import replace

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Document, DocumentChunk
from app.retrieval.hybrid import RetrievedChunk

TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def bm25_rank(query: str, chunks: list[RetrievedChunk], top_k: int, k1: float = 1.5, b: float = 0.75):
    query_terms = tokenize(query)
    if not query_terms or not chunks:
        return []

    tokenized = [tokenize(chunk.text) for chunk in chunks]
    avg_len = sum(len(tokens) for tokens in tokenized) / max(len(tokenized), 1)
    doc_freq: Counter[str] = Counter()
    for tokens in tokenized:
        doc_freq.update(set(tokens))

    ranked: list[RetrievedChunk] = []
    total_docs = len(chunks)
    for chunk, tokens in zip(chunks, tokenized, strict=True):
        frequencies = Counter(tokens)
        score = 0.0
        doc_len = len(tokens) or 1
        for term in query_terms:
            if term not in frequencies:
                continue
            idf = math.log(1 + (total_docs - doc_freq[term] + 0.5) / (doc_freq[term] + 0.5))
            numerator = frequencies[term] * (k1 + 1)
            denominator = frequencies[term] + k1 * (1 - b + b * doc_len / max(avg_len, 1))
            score += idf * numerator / denominator
        if score > 0:
            ranked.append(replace(chunk, score=round(score, 4)))

    return sorted(ranked, key=lambda item: item.score, reverse=True)[:top_k]


async def keyword_search(
    db: AsyncSession,
    query: str,
    workspace_id: str | None,
    top_k: int,
) -> list[RetrievedChunk]:
    stmt = (
        select(DocumentChunk, Document)
        .join(Document, Document.id == DocumentChunk.document_id)
        .order_by(DocumentChunk.created_at.desc())
        .limit(500)
    )
    if workspace_id:
        stmt = stmt.where(DocumentChunk.workspace_id == workspace_id)

    rows = (await db.execute(stmt)).all()
    chunks = [
        RetrievedChunk(
            chunk_id=chunk.chroma_id,
            document_id=document.id,
            document_title=document.title,
            workspace_id=chunk.workspace_id,
            text=chunk.text,
            page_number=chunk.page_number,
            source=document.source,
            score=0.0,
            metadata=chunk.chunk_metadata,
        )
        for chunk, document in rows
    ]
    return bm25_rank(query, chunks, top_k=top_k)
