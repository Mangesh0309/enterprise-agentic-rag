from __future__ import annotations

from app.agents.state import AgentState


def judge_answer(primary: AgentState, challenger: AgentState | None = None) -> AgentState:
    if challenger is None:
        return primary
    if challenger.get("confidence_score", 0) > primary.get("confidence_score", 0):
        return challenger
    return primary
