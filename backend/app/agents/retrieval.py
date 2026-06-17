from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.state import AgentCitation, AgentState
from app.core.config import get_settings
from app.retrieval.bm25 import keyword_search
from app.retrieval.chroma import dense_search
from app.retrieval.hybrid import weighted_merge


async def retrieve_context(state: AgentState, db: AsyncSession) -> AgentState:
    settings = get_settings()
    if state.get("route") == "web":
        return state

    dense = dense_search(state["query"], state.get("workspace_id"), settings.retrieval_top_k)
    keyword = await keyword_search(db, state["query"], state.get("workspace_id"), settings.retrieval_top_k)
    results = weighted_merge(
        dense,
        keyword,
        dense_weight=settings.hybrid_dense_weight,
        keyword_weight=settings.hybrid_bm25_weight,
        top_k=settings.retrieval_top_k,
    )

    citations: list[AgentCitation] = [
        {
            "document_id": item.document_id,
            "document_title": item.document_title,
            "chunk_id": item.chunk_id,
            "page_number": item.page_number,
            "passage": item.text,
            "score": item.score,
            "source_url": item.source,
        }
        for item in results
    ]
    return {
        **state,
        "contexts": citations,
        "retrieval_path": state.get("retrieval_path", [])
        + [{"agent": "retrieval", "dense": len(dense), "keyword": len(keyword), "returned": len(results)}],
    }
