from typing import Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.api import deps
from app.models.user import User
from app.models.job import JobSource
from app.schemas.ingest import IngestTriggerRequest, IngestStatus
from app.workers.job_ingest_worker import run_ingestion_task

router = APIRouter()

@router.post("/trigger", response_model=IngestStatus)
async def trigger_ingestion(
    request: IngestTriggerRequest,
    current_user: User = Depends(deps.get_current_active_superuser),
    db: AsyncSession = Depends(deps.get_session)
) -> Any:
    """
    Trigger a job ingestion task.
    Upserts a JobSource config and dispatches a Celery task.
    """
    # 1. Check or Create Source
    result = await db.execute(select(JobSource).where(JobSource.name == request.source_name))
    source = result.scalars().first()
    
    if not source:
        source = JobSource(
            name=request.source_name,
            type=request.source_type,
            base_url=request.base_url,
            config=request.config
        )
        db.add(source)
    else:
        # Update config
        source.type = request.source_type
        source.base_url = request.base_url
        source.config = request.config
        db.add(source)
    
    await db.commit()
    await db.refresh(source)
    
    # 2. Trigger Celery Task
    task = run_ingestion_task.delay(source.id)
    
    return IngestStatus(
        task_id=task.id,
        status="queued"
    )
