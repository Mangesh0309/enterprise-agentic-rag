from typing import Any, Literal, TypedDict


class AgentCitation(TypedDict, total=False):
    document_id: str
    document_title: str
    chunk_id: str
    page_number: int
    passage: str
    score: float
    source_url: str


class AgentState(TypedDict, total=False):
    query: str
    workspace_id: str | None
    conversation_id: str | None
    history: list[dict[str, str]]
    use_web: bool
    route: Literal["internal", "web", "hybrid"]
    contexts: list[AgentCitation]
    web_results: list[dict[str, Any]]
    answer: str
    confidence_score: float
    unsupported_claims: list[str]
    needs_retry: bool
    reflection_cycles: int
    retrieval_path: list[dict[str, Any]]
    tool_usage: list[dict[str, Any]]
