from __future__ import annotations

from app.agents.state import AgentState
from app.core.config import get_settings


async def search_web(state: AgentState) -> AgentState:
    if state.get("route") == "internal" or not state.get("use_web", True):
        return state

    settings = get_settings()
    if not settings.tavily_api_key:
        return {
            **state,
            "web_results": [],
            "tool_usage": state.get("tool_usage", [])
            + [{"tool": "tavily", "status": "skipped", "reason": "missing_api_key"}],
        }

    from tavily import AsyncTavilyClient

    client = AsyncTavilyClient(api_key=settings.tavily_api_key)
    response = await client.search(
        query=state["query"],
        max_results=settings.tavily_max_results,
        search_depth="advanced",
        include_answer=False,
    )
    results = response.get("results", [])
    return {
        **state,
        "web_results": results,
        "tool_usage": state.get("tool_usage", []) + [{"tool": "tavily", "results": len(results)}],
    }
