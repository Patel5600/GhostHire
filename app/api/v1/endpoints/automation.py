from typing import Any
from datetime import datetime
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.models.user import User
from app.models.job import Job
from app.models.resume import Resume
from app.models.automation import ApplicationRun
from app.services.automation.appliers import GreenhouseApplier, LeverApplier

router = APIRouter()

async def run_application_task(run_id: int, user_id: int, job_id: int, session_factory):
    """
    Background worker process.
    """
    from sqlalchemy.orm import selectinload
    
    async with session_factory() as db:
        run = await db.get(ApplicationRun, run_id)
        if not run: return
        
        run.status = "running"
        await db.commit()
        
        try:
            # Fetch user and resume info (simplified)
            user = await db.get(User, user_id)
            job = await db.get(Job, job_id)
            
            # Find primary resume
            resume_res = await db.execute(select(Resume).where(Resume.user_id == user_id).limit(1))
            resume = resume_res.scalars().first()
            
            if not resume:
                raise Exception("No resume found")
            
            # Determine applier
            applier = None
            if "greenhouse" in job.url:
                applier = GreenhouseApplier(user, resume.file_path or "mock.pdf")
            elif "lever" in job.url:
                applier = LeverApplier(user, resume.file_path or "mock.pdf")
            else:
                raise Exception("Unsupported ATS")

            success = await applier.apply(job.url)
            
            run.status = "success" if success else "failed"
            run.log_summary = "Application submitted successfully" if success else "Submission failed or form unknown"
            
        except Exception as e:
            run.status = "failed"
            run.log_summary = str(e)
        
        run.completed_at = datetime.utcnow()
        await db.commit()

@router.post("/apply/{job_id}")
async def trigger_application(
    job_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Trigger an automated application run.
    """
    # Verify Job
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found")

    # Create Run Record
    run = ApplicationRun(
        user_id=current_user.id,
        job_id=job.id,
        status="pending"
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    # Queue background task
    from app.db.session import engine
    from sqlalchemy.orm import sessionmaker
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    background_tasks.add_task(run_application_task, run.id, current_user.id, job.id, async_session)

    return {"message": "Application queued", "run_id": run.id}
