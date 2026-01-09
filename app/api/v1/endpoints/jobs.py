from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.models.job import Job
from app.schemas.job import JobCreate, JobRead

router = APIRouter()

@router.get("/", response_model=List[JobRead])
async def read_jobs(
    db: AsyncSession = Depends(deps.get_session),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve jobs.
    """
    result = await db.execute(select(Job).offset(skip).limit(limit))
    jobs = result.scalars().all()
    return jobs

@router.post("/", response_model=JobRead)
async def create_job(
    *,
    db: AsyncSession = Depends(deps.get_session),
    job_in: JobCreate,
    current_user: Any = Depends(deps.get_current_user), # Require auth
) -> Any:
    """
    Create new job.
    """
    job = Job.from_orm(job_in)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job
