from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_admin
from app.db.models import Document, User, UserRole
from app.db.session import get_db
from app.schemas.documents import DocumentRead
from app.services.document_service import ingest_upload, list_documents, remove_document

router = APIRouter()


async def _can_access_workspace(user: User, workspace_id: str, db: AsyncSession) -> bool:
    from sqlalchemy import select

    from app.db.models import WorkspaceMember

    if user.role == UserRole.admin:
        return True
    member = (
        await db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user.id,
            )
        )
    ).scalar_one_or_none()
    return member is not None


@router.post("/upload", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    workspace_id: str = Form(...),
    category: str | None = Form(None),
    file: UploadFile = File(...),
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Document:
    return await ingest_upload(db, file, workspace_id=workspace_id, category=category)


@router.get("", response_model=list[DocumentRead])
async def documents(
    workspace_id: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Document]:
    if workspace_id and not await _can_access_workspace(user, workspace_id, db):
        raise HTTPException(status_code=403, detail="Workspace access denied")
    return await list_documents(db, workspace_id)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> None:
    await remove_document(db, document_id)
