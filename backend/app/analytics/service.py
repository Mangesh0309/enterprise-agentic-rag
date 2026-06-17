from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AgentTrace, Document, DocumentStatus, Feedback, Message, MessageRole
from app.schemas.analytics import AnalyticsSummary, DocumentAccessStat


async def get_summary(db: AsyncSession) -> AnalyticsSummary:
    total_queries = (await db.execute(select(func.count(AgentTrace.id)))).scalar_one()
    average_latency = (await db.execute(select(func.avg(AgentTrace.latency_ms)))).scalar_one() or 0
    retrieval_successes = (
        await db.execute(select(func.count(AgentTrace.id)).where(AgentTrace.final_confidence >= 0.72))
    ).scalar_one()
    avg_feedback = (await db.execute(select(func.avg(Feedback.rating)))).scalar_one()
    indexed_docs = (
        await db.execute(select(func.count(Document.id)).where(Document.status == DocumentStatus.indexed))
    ).scalar_one()
    return AnalyticsSummary(
        total_queries=total_queries,
        average_latency_ms=round(float(average_latency), 2),
        retrieval_success_rate=round(retrieval_successes / total_queries, 4) if total_queries else 0.0,
        average_feedback_score=round(float(avg_feedback), 2) if avg_feedback is not None else None,
        documents_indexed=indexed_docs,
    )


async def get_document_access_stats(db: AsyncSession) -> list[DocumentAccessStat]:
    documents = (await db.execute(select(Document))).scalars().all()
    messages = (await db.execute(select(Message).where(Message.role == MessageRole.assistant))).scalars().all()

    counts = {document.id: 0 for document in documents}
    titles = {document.id: document.title for document in documents}
    for message in messages:
        for citation in message.citations or []:
            document_id = citation.get("document_id")
            if document_id in counts:
                counts[document_id] += 1

    ranked = sorted(counts.items(), key=lambda pair: pair[1], reverse=True)[:10]
    return [
        DocumentAccessStat(document_id=document_id, title=titles[document_id], access_count=count)
        for document_id, count in ranked
    ]
