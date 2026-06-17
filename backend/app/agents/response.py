from __future__ import annotations

import httpx

from app.agents.state import AgentState
from app.core.config import get_settings


def _format_context(state: AgentState) -> str:
    internal = []
    for index, item in enumerate(state.get("contexts", []), start=1):
        label = item.get("document_title") or item.get("source_url") or "Internal source"
        page = f", page {item['page_number']}" if item.get("page_number") else ""
        internal.append(f"[{index}] {label}{page}\n{item.get('passage', '')}")

    offset = len(internal)
    web = []
    for index, item in enumerate(state.get("web_results", []), start=offset + 1):
        web.append(f"[{index}] {item.get('title')}\nURL: {item.get('url')}\n{item.get('content')}")

    return "\n\n".join(internal + web) or "No supporting context was retrieved."


def build_prompt(state: AgentState) -> str:
    history = "\n".join(
        f"{message['role']}: {message['content']}" for message in state.get("history", [])[-6:]
    )
    return f"""You are an enterprise knowledge assistant.
Answer professionally and concisely using only the provided evidence.
If evidence is insufficient, say what is missing.
Include citation markers like [1], [2] for supported claims.

Conversation history:
{history or "No previous messages."}

Evidence:
{_format_context(state)}

Question:
{state["query"]}

Answer:"""


async def generate_response(state: AgentState) -> AgentState:
    settings = get_settings()
    prompt = build_prompt(state)
    async with httpx.AsyncClient(timeout=settings.ollama_request_timeout) as client:
        response = await client.post(
            f"{settings.ollama_base_url}/api/generate",
            json={"model": settings.ollama_model, "prompt": prompt, "stream": False},
        )
        response.raise_for_status()
        payload = response.json()

    return {
        **state,
        "answer": payload.get("response", "").strip(),
        "tool_usage": state.get("tool_usage", []) + [{"tool": "ollama", "model": settings.ollama_model}],
    }
