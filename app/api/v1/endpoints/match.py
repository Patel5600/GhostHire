from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Any
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel
from app.api import deps
from app.services.matching.engine import MatchingEngine
from app.models.match import MatchResult

router = APIRouter()

class MatchRequest(BaseModel):
    resume_id: int
    job_id: int

@router.post("/run", response_model=MatchResult)
async def run_matching(
    request: MatchRequest,
    db: AsyncSession = Depends(deps.get_session),
    current_user: Any = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    Run the matching engine for a specific Resume and Job.
    """
    engine = MatchingEngine(db)
    try:
        result = await engine.run_match(request.resume_id, request.job_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
