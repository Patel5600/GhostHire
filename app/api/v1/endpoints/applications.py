from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.api import deps
from app.models.application import Application
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationRead

router = APIRouter()

@router.get("/", response_model=List[ApplicationRead])
async def read_applications(
    db: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve applications for current user.
    """
    # Use selectinload to fetch related Job data
    stmt = (
        select(Application)
        .where(Application.user_id == current_user.id)
        .options(selectinload(Application.job))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    applications = result.scalars().all()
    return applications

@router.post("/", response_model=ApplicationRead)
async def create_application(
    *,
    db: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
    application_in: ApplicationCreate,
) -> Any:
    """
    Create new application (Apply to a job).
    """
    # Check if already applied
    stmt = select(Application).where(
        Application.user_id == current_user.id, 
        Application.job_id == application_in.job_id
    )
    result = await db.execute(stmt)
    if result.scalars().first():
         raise HTTPException(400, "Already applied to this job")

    application = Application(
        user_id=current_user.id,
        **application_in.dict()
    )
    db.add(application)
    await db.commit()
    await db.refresh(application)
    return application
