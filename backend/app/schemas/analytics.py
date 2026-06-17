from pydantic import BaseModel


class AnalyticsSummary(BaseModel):
    total_queries: int
    average_latency_ms: float
    retrieval_success_rate: float
    average_feedback_score: float | None
    documents_indexed: int


class DocumentAccessStat(BaseModel):
    document_id: str
    title: str
    access_count: int
