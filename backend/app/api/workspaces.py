from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_admin
from app.db.models import User, UserRole, Workspace, WorkspaceMember
from app.db.session import get_db
from app.schemas.workspaces import WorkspaceCreate, WorkspaceRead

router = APIRouter()


@router.post("", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    payload: WorkspaceCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Workspace:
    workspace = Workspace(**payload.model_dump())
    db.add(workspace)
    await db.commit()
    await db.refresh(workspace)
    return workspace


@router.get("", response_model=list[WorkspaceRead])
async def list_workspaces(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Workspace]:
    stmt = select(Workspace).order_by(Workspace.name)
    if user.role != UserRole.admin:
        stmt = stmt.join(WorkspaceMember).where(WorkspaceMember.user_id == user.id)
    return list((await db.execute(stmt)).scalars().all())


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: str,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> None:
    workspace = await db.get(Workspace, workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    await db.delete(workspace)
    await db.commit()


@router.post("/{workspace_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_workspace_member(
    workspace_id: str,
    user_id: str,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> None:
    if await db.get(Workspace, workspace_id) is None or await db.get(User, user_id) is None:
        raise HTTPException(status_code=404, detail="Workspace or user not found")
    exists = (
        await db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
        )
    ).scalar_one_or_none()
    if exists is None:
        db.add(WorkspaceMember(workspace_id=workspace_id, user_id=user_id))
        await db.commit()
