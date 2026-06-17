from __future__ import annotations

import re

from app.agents.state import AgentState
from app.core.config import get_settings

CITATION_RE = re.compile(r"\[(\d+)\]")


def verify_answer(state: AgentState) -> AgentState:
    answer = state.get("answer", "")
    contexts = state.get("contexts", [])
    web_results = state.get("web_results", [])
    evidence_count = len(contexts) + len(web_results)
    citations = [int(match) for match in CITATION_RE.findall(answer)]

    citation_score = 1.0 if citations else 0.35
    valid_citations = [citation for citation in citations if 1 <= citation <= max(evidence_count, 1)]
    validity_score = len(valid_citations) / max(len(citations), 1)
    support_score = min(1.0, evidence_count / 3) if evidence_count else 0.15
    confidence = round((citation_score * 0.35) + (validity_score * 0.25) + (support_score * 0.4), 4)

    unsupported_claims = []
    if evidence_count == 0:
        unsupported_claims.append("No evidence retrieved.")
    if not citations:
        unsupported_claims.append("Answer does not include citation markers.")

    settings = get_settings()
    cycles = state.get("reflection_cycles", 0)
    needs_retry = confidence < settings.min_verification_score and cycles < settings.max_reflection_cycles
    return {
        **state,
        "confidence_score": confidence,
        "unsupported_claims": unsupported_claims,
        "needs_retry": needs_retry,
        "retrieval_path": state.get("retrieval_path", [])
        + [{"agent": "verification", "confidence": confidence, "needs_retry": needs_retry}],
    }
