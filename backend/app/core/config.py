from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Enterprise Agentic RAG"
    app_env: Literal["local", "test", "staging", "production"] = "local"
    api_prefix: str = "/api"
    backend_cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    database_url: str = "postgresql+asyncpg://rag:rag@localhost:5432/enterprise_rag"
    sync_database_url: str = "postgresql://rag:rag@localhost:5432/enterprise_rag"

    chroma_host: str = "localhost"
    chroma_port: int = 8001
    chroma_collection: str = "enterprise_knowledge"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    ollama_request_timeout: int = 120

    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_batch_size: int = 32

    tavily_api_key: str | None = None
    tavily_max_results: int = 5

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    retrieval_top_k: int = 6
    hybrid_dense_weight: float = 0.65
    hybrid_bm25_weight: float = 0.35
    chunk_size: int = 900
    chunk_overlap: int = 120
    max_reflection_cycles: int = 2
    min_verification_score: float = 0.72

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
