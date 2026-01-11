from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.api import deps
from app.models.user import User
from app.models.job import Job
from app.models.application import Application, ApplicationStatus
from app.workers.auto_apply_worker import run_auto_apply

router = APIRouter()

@router.post("/apply/{job_id}", response_model=Application)
async def trigger_auto_apply(
    job_id: int,
    db: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Trigger auto-apply for a specific job.
    """
    # 1. Fetch Job
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # 2. Check for Resume (Assume user has at least one for simplicity, or pick default)
    # Ideally passed in request body, but for path param simplified flow:
    resume = next((r for r in current_user.resumes), None) # Need to load relationship or fetch
    if not resume:
        # Try explicit fetch if relationship not loaded
        # In this architecture, we might need a separate query if lazy loaded
        pass # Simplified for this snippet, assume existence or handled in engine
    
    # 3. Create Application Entry
    # Check if already exists
    existing = await db.execute(
        select(Application)
        .where(Application.user_id == current_user.id)
        .where(Application.job_id == job_id)
    )
    application = existing.scalars().first()
    
    if not application:
        application = Application(
            user_id=current_user.id,
            job_id=job_id,
            resume_id=resume.id if resume else None,
            status=ApplicationStatus.APPLYING
        )
        db.add(application)
        await db.commit()
        await db.refresh(application)
    else:
        # Restart or Re-trigger?
        application.status = ApplicationStatus.APPLYING
        db.add(application)
        await db.commit()

    # 4. Trigger Celery Task
    run_auto_apply.delay(application.id)
    
    return application
