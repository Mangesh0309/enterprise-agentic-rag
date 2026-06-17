from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Conversation, Message


async def get_recent_history(db: AsyncSession, conversation_id: str | None, limit: int = 10):
    if not conversation_id:
        return []
    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    rows = list((await db.execute(stmt)).scalars().all())
    rows.reverse()
    return [{"role": message.role.value, "content": message.content} for message in rows]


async def get_or_create_conversation(
    db: AsyncSession,
    user_id: str,
    workspace_id: str | None,
    conversation_id: str | None,
    title_seed: str,
) -> Conversation:
    if conversation_id:
        conversation = await db.get(Conversation, conversation_id)
        if conversation:
            return conversation

    conversation = Conversation(
        user_id=user_id,
        workspace_id=workspace_id,
        title=title_seed[:90] or "New conversation",
    )
    db.add(conversation)
    await db.flush()
    return conversation
