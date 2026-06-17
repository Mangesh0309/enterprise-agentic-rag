from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(slots=True)
class RetrievedChunk:
    chunk_id: str
    document_id: str
    document_title: str
    workspace_id: str
    text: str
    score: float
    page_number: int | None = None
    source: str | None = None
    metadata: dict | None = None


def weighted_merge(
    dense_results: list[RetrievedChunk],
    keyword_results: list[RetrievedChunk],
    dense_weight: float,
    keyword_weight: float,
    top_k: int,
) -> list[RetrievedChunk]:
    scores: dict[str, float] = {}
    chunks: dict[str, RetrievedChunk] = {}

    def normalized(results: list[RetrievedChunk]) -> list[tuple[RetrievedChunk, float]]:
        if not results:
            return []
        max_score = max(item.score for item in results) or 1.0
        return [(item, item.score / max_score) for item in results]

    for item, score in normalized(dense_results):
        chunks[item.chunk_id] = item
        scores[item.chunk_id] = scores.get(item.chunk_id, 0.0) + score * dense_weight

    for item, score in normalized(keyword_results):
        chunks[item.chunk_id] = item
        scores[item.chunk_id] = scores.get(item.chunk_id, 0.0) + score * keyword_weight

    ranked = sorted(scores.items(), key=lambda pair: pair[1], reverse=True)[:top_k]
    return [replace(chunks[chunk_id], score=round(score, 4)) for chunk_id, score in ranked]
