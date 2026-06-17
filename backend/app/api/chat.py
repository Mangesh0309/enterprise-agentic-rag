from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.db.models import User, UserRole, WorkspaceMember
from app.db.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import answer_chat

router = APIRouter()


async def _assert_workspace_access(db: AsyncSession, user: User, workspace_id: str | None) -> None:
    if workspace_id is None or user.role == UserRole.admin:
        return
    member = (
        await db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user.id,
            )
        )
    ).scalar_one_or_none()
    if member is None:
        raise HTTPException(status_code=403, detail="Workspace access denied")


@router.post("", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    await _assert_workspace_access(db, user, payload.workspace_id)
    return await answer_chat(db, payload, user)


@router.post("/stream")
async def stream_chat(
    payload: ChatRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    await _assert_workspace_access(db, user, payload.workspace_id)

    async def events():
        try:
            result = await answer_chat(db, payload, user)
            for character in result.answer:
                yield f"event: token\ndata: {json.dumps({'token': character})}\n\n"
            yield f"event: done\ndata: {result.model_dump_json()}\n\n"
        except Exception as exc:
            yield f"event: error\ndata: {json.dumps({'detail': str(exc)})}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")
