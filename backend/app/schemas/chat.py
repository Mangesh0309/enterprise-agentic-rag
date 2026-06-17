from pydantic import BaseModel, Field

from app.schemas.documents import Citation


class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=6000)
    workspace_id: str | None = None
    conversation_id: str | None = None
    use_web: bool = True


class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    answer: str
    citations: list[Citation]
    confidence_score: float
    route: str
    reflection_cycles: int
