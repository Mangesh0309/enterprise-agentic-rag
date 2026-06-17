from __future__ import annotations

import time

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import run_agent_graph
from app.db.models import AgentTrace, Message, MessageRole, User
from app.memory.store import get_or_create_conversation, get_recent_history
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.documents import Citation


async def answer_chat(db: AsyncSession, request: ChatRequest, user: User) -> ChatResponse:
    started = time.perf_counter()
    conversation = await get_or_create_conversation(
        db,
        user_id=user.id,
        workspace_id=request.workspace_id,
        conversation_id=request.conversation_id,
        title_seed=request.query,
    )
    history = await get_recent_history(db, conversation.id)

    user_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.user,
        content=request.query,
    )
    db.add(user_message)
    await db.flush()

    state = await run_agent_graph(
        {
            "query": request.query,
            "workspace_id": request.workspace_id,
            "conversation_id": conversation.id,
            "history": history,
            "use_web": request.use_web,
            "reflection_cycles": 0,
            "contexts": [],
            "web_results": [],
            "retrieval_path": [],
            "tool_usage": [],
        },
        db,
    )

    latency_ms = int((time.perf_counter() - started) * 1000)
    trace = AgentTrace(
        conversation_id=conversation.id,
        user_id=user.id,
        query=request.query,
        route=state.get("route", "internal"),
        retrieval_path=state.get("retrieval_path", []),
        tool_usage=state.get("tool_usage", []),
        reflection_cycles=state.get("reflection_cycles", 0),
        latency_ms=latency_ms,
        final_confidence=state.get("confidence_score"),
    )
    db.add(trace)
    await db.flush()

    citations = [
        Citation(
            document_id=item.get("document_id"),
            document_title=item.get("document_title"),
            chunk_id=item.get("chunk_id"),
            page_number=item.get("page_number"),
            passage=item.get("passage", ""),
            score=item.get("score"),
            source_url=item.get("source_url"),
        )
        for item in state.get("contexts", [])
    ]

    assistant_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.assistant,
        content=state.get("answer", ""),
        citations=[citation.model_dump() for citation in citations],
        confidence_score=state.get("confidence_score", 0.0),
        agent_trace_id=trace.id,
    )
    db.add(assistant_message)
    await db.commit()
    await db.refresh(assistant_message)

    return ChatResponse(
        conversation_id=conversation.id,
        message_id=assistant_message.id,
        answer=assistant_message.content,
        citations=citations,
        confidence_score=assistant_message.confidence_score or 0.0,
        route=trace.route,
        reflection_cycles=trace.reflection_cycles,
    )
