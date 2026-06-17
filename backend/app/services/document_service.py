from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Document, DocumentChunk, DocumentStatus
from app.ingestion.pipeline import checksum_bytes, parse_and_chunk
from app.retrieval.chroma import delete_document_vectors, upsert_chunks


async def list_documents(db: AsyncSession, workspace_id: str | None = None) -> list[Document]:
    stmt = select(Document).order_by(Document.created_at.desc())
    if workspace_id:
        stmt = stmt.where(Document.workspace_id == workspace_id)
    return list((await db.execute(stmt)).scalars().all())


async def ingest_upload(
    db: AsyncSession,
    upload: UploadFile,
    workspace_id: str,
    category: str | None = None,
) -> Document:
    data = await upload.read()
    checksum = checksum_bytes(data)

    existing = (
        await db.execute(
            select(Document).where(Document.workspace_id == workspace_id, Document.checksum == checksum)
        )
    ).scalar_one_or_none()
    if existing and existing.status == DocumentStatus.indexed:
        return existing

    document = Document(
        workspace_id=workspace_id,
        title=upload.filename or "Untitled document",
        source=upload.filename or "upload",
        content_type=upload.content_type or "application/octet-stream",
        checksum=checksum,
        category=category,
        status=DocumentStatus.pending,
        doc_metadata={"upload_filename": upload.filename},
    )
    db.add(document)
    await db.flush()

    suffix = Path(upload.filename or "upload.txt").suffix or ".txt"
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(data)
            temp_path = temp_file.name

        parsed, chunks = parse_and_chunk(temp_path, document.content_type)
        document.page_count = len(parsed.pages)
        document.doc_metadata = {**document.doc_metadata, **parsed.metadata}

        chroma_payload: list[dict] = []
        for chunk in chunks:
            chroma_id = f"{document.id}:{chunk.position}"
            db.add(
                DocumentChunk(
                    workspace_id=workspace_id,
                    document_id=document.id,
                    chroma_id=chroma_id,
                    text=chunk.text,
                    page_number=chunk.page_number,
                    position=chunk.position,
                    token_count=chunk.token_count,
                    chunk_metadata=chunk.metadata,
                )
            )
            chroma_payload.append(
                {
                    "id": chroma_id,
                    "text": chunk.text,
                    "metadata": {
                        "workspace_id": workspace_id,
                        "document_id": document.id,
                        "document_title": document.title,
                        "page_number": chunk.page_number or 0,
                        "source": document.source,
                        "category": category or "",
                        "position": chunk.position,
                    },
                }
            )

        upsert_chunks(chroma_payload)
        document.status = DocumentStatus.indexed
        await db.commit()
        await db.refresh(document)
        return document
    except Exception as exc:
        document.status = DocumentStatus.failed
        document.error_message = str(exc)
        await db.commit()
        await db.refresh(document)
        return document
    finally:
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)


async def remove_document(db: AsyncSession, document_id: str) -> None:
    await db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document_id))
    await db.execute(delete(Document).where(Document.id == document_id))
    delete_document_vectors(document_id)
    await db.commit()
