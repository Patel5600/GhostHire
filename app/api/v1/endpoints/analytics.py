from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api import deps
from app.models.user import User
from app.services.analytics.engine import analytics_engine

router = APIRouter()

@router.post("/ingest")
async def ingest_analytics(
    db: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Force manual ingestion/sync of application metrics.
    """
    await analytics_engine.ingest_outcomes(db, current_user.id)
    return {"message": "Analytics ingested"}

@router.get("/user-insights")
async def get_insights(
    db: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> Dict[str, Any]:
    """
    Get high-level user insights.
    """
    # Ensure fresh data
    await analytics_engine.ingest_outcomes(db, current_user.id)
    return await analytics_engine.generate_insights(db, current_user.id)

@router.post("/predict")
async def predict_match(
    resume_text: str,
    job_desc: str,
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get a statistical prediction of success for a specific pair.
    """
    score = await analytics_engine.predict_success(job_desc, resume_text)
    return {"predicted_success_probability": score}
