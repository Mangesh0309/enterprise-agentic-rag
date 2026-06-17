from pydantic import BaseModel, Field


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = None
    category: str | None = None


class WorkspaceRead(BaseModel):
    id: str
    name: str
    description: str | None
    category: str | None

    model_config = {"from_attributes": True}
