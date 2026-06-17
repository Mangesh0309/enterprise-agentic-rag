from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import EvaluationReport


async def create_placeholder_report(
    db: AsyncSession,
    name: str,
    workspace_id: str | None,
) -> EvaluationReport:
    # RAGAS needs curated question/ground-truth datasets. This report records the metric contract
    # and gives teams a stable artifact before they upload an evaluation set.
    metrics = {
        "faithfulness": None,
        "answer_relevancy": None,
        "context_precision": None,
        "context_recall": None,
    }
    report = {
        "status": "dataset_required",
        "message": "Upload a labeled evaluation dataset to compute RAGAS metrics.",
    }
    item = EvaluationReport(name=name, workspace_id=workspace_id, metrics=metrics, report=report)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item
