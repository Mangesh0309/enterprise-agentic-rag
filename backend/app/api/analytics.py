from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.service import get_document_access_stats, get_summary
from app.auth.dependencies import require_admin
from app.db.models import User
from app.db.session import get_db
from app.schemas.analytics import AnalyticsSummary, DocumentAccessStat

router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummary)
async def summary(
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> AnalyticsSummary:
    return await get_summary(db)


@router.get("/documents", response_model=list[DocumentAccessStat])
async def document_stats(
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> list[DocumentAccessStat]:
    return await get_document_access_stats(db)
