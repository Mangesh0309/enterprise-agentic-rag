from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.db.models import Feedback, User
from app.db.session import get_db
from app.schemas.feedback import FeedbackCreate, FeedbackRead

router = APIRouter()


@router.post("", response_model=FeedbackRead, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    payload: FeedbackCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Feedback:
    feedback = Feedback(message_id=payload.message_id, user_id=user.id, rating=payload.rating, comment=payload.comment)
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    return feedback
