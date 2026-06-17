from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_admin
from app.db.models import EvaluationReport, User
from app.db.session import get_db
from app.evaluation.ragas_runner import create_placeholder_report

router = APIRouter()


class EvaluationRunRequest(BaseModel):
    name: str = "Baseline RAGAS evaluation"
    workspace_id: str | None = None


class EvaluationReportRead(BaseModel):
    id: str
    name: str
    workspace_id: str | None
    metrics: dict
    report: dict

    model_config = {"from_attributes": True}


@router.post("/run", response_model=EvaluationReportRead)
async def run_evaluation(
    payload: EvaluationRunRequest,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> EvaluationReport:
    return await create_placeholder_report(db, payload.name, payload.workspace_id)
