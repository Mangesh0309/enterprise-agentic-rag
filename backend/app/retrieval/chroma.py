from __future__ import annotations

from functools import lru_cache

import chromadb
from sentence_transformers import SentenceTransformer

from app.core.config import get_settings
from app.retrieval.hybrid import RetrievedChunk


@lru_cache
def get_embedder() -> SentenceTransformer:
    settings = get_settings()
    return SentenceTransformer(settings.embedding_model)


@lru_cache
def get_collection():
    settings = get_settings()
    client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)
    return client.get_or_create_collection(settings.chroma_collection)


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    embeddings = get_embedder().encode(texts, normalize_embeddings=True)
    return [embedding.tolist() for embedding in embeddings]


def upsert_chunks(chunks: list[dict]) -> None:
    if not chunks:
        return
    collection = get_collection()
    texts = [chunk["text"] for chunk in chunks]
    collection.upsert(
        ids=[chunk["id"] for chunk in chunks],
        documents=texts,
        embeddings=embed_texts(texts),
        metadatas=[chunk["metadata"] for chunk in chunks],
    )


def delete_document_vectors(document_id: str) -> None:
    collection = get_collection()
    collection.delete(where={"document_id": document_id})


def dense_search(query: str, workspace_id: str | None, top_k: int) -> list[RetrievedChunk]:
    collection = get_collection()
    where = {"workspace_id": workspace_id} if workspace_id else None
    results = collection.query(
        query_embeddings=embed_texts([query]),
        n_results=top_k,
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    chunks: list[RetrievedChunk] = []
    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for chunk_id, text, metadata, distance in zip(ids, docs, metadatas, distances, strict=False):
        score = max(0.0, 1.0 - float(distance))
        chunks.append(
            RetrievedChunk(
                chunk_id=chunk_id,
                document_id=metadata.get("document_id"),
                document_title=metadata.get("document_title"),
                workspace_id=metadata.get("workspace_id"),
                text=text,
                page_number=metadata.get("page_number"),
                source=metadata.get("source"),
                score=round(score, 4),
                metadata=metadata,
            )
        )
    return chunks
