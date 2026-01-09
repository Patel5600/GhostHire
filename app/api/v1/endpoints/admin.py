from typing import Any, Dict, List
from fastapi import APIRouter, Depends, Query, Body

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.models.user import User, UserRole
from app.models.admin import AuditLog
from app.services.admin_service import admin_service
from app.core.permissions import verify_admin_access, verify_superadmin_access

router = APIRouter()

@router.get("/metrics", dependencies=[Depends(verify_admin_access)])
async def get_system_metrics(
    db: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> Dict:
    """
    Get holistic system overview.
    """
    return await admin_service.get_system_metrics(db)

@router.get("/users", dependencies=[Depends(verify_admin_access)])
async def list_users(
    db: AsyncSession = Depends(deps.get_session),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
):
    """
    List all users (Admin view).
    """
    res = await db.execute(select(User).offset(skip).limit(limit))
    return res.scalars().all()

@router.post("/pipeline/control", dependencies=[Depends(verify_superadmin_access)])
async def control_pipeline(
    action: str = Body(...), # "stop_all", "pause_user"
    target_id: int = Body(..., embed=True),
    db: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Emergency controls for pipelines.
    """
    # Log Action
    log = AuditLog(
        user_id=current_user.id,
        action=action,
        target_resource=str(target_id),
        details={"action": action}
    )
    db.add(log)
    await db.commit()

    if action == "stop_all":
        # Logic to kill all celery tasks would go here
        return {"message": "All pipelines stop signal sent"}
    
    return {"message": "Action logged"}
