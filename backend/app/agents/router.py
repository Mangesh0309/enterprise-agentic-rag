from __future__ import annotations

import re

from app.agents.state import AgentState

CURRENTNESS_TERMS = re.compile(
    r"\b(today|latest|recent|current|now|this week|this month|news|stock|price|release|law|regulation)\b",
    re.IGNORECASE,
)


def route_query(state: AgentState) -> AgentState:
    query = state["query"]
    has_workspace = bool(state.get("workspace_id"))
    use_web = state.get("use_web", True)
    needs_current = bool(CURRENTNESS_TERMS.search(query))

    if has_workspace and use_web and needs_current:
        route = "hybrid"
    elif has_workspace:
        route = "internal"
    elif use_web:
        route = "web"
    else:
        route = "internal"

    return {
        **state,
        "route": route,
        "retrieval_path": state.get("retrieval_path", []) + [{"agent": "router", "route": route}],
    }
