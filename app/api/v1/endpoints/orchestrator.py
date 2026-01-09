from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.models.user import User
from app.models.workflow import WorkflowRun
from app.services.orchestrator.engine import orchestrator

router = APIRouter()

@router.post("/start-pipeline")
async def start_pipeline(
    workflow_name: str,
    payload: Dict[str, Any],
    db: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Start a workflow pipeline.
    Example payload: {"url": "https://..."}
    """
    run_id = await orchestrator.start_pipeline(db, workflow_name, current_user.id, payload)
    return {"message": "Pipeline started", "pipeline_id": run_id}

@router.get("/status/{pipeline_id}")
async def get_status(
    pipeline_id: int,
    db: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
):
    run = await db.get(WorkflowRun, pipeline_id)
    if not run:
        return {"error": "Pipeline not found"}
    return run
