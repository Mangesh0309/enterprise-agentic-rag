from datetime import datetime

from pydantic import BaseModel

from app.db.models import DocumentStatus


class DocumentRead(BaseModel):
    id: str
    workspace_id: str
    title: str
    source: str
    content_type: str
    category: str | None
    status: DocumentStatus
    page_count: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Citation(BaseModel):
    document_id: str | None = None
    document_title: str | None = None
    chunk_id: str | None = None
    page_number: int | None = None
    passage: str
    score: float | None = None
    source_url: str | None = None
