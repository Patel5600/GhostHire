from typing import Any, Dict
from fastapi import APIRouter, Depends, Body, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.models.user import User
from app.models.resume import Resume
from app.services.ai.service import ai_manager

router = APIRouter()

@router.post("/optimize-resume")
async def optimize_resume(
    *,
    db: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
    resume_id: int = Body(..., embed=True),
    job_description: str = Body(..., embed=True),
) -> Dict[str, Any]:
    """
    Optimize a resume for a specific job description.
    """
    # Fetch Resume
    result = await db.execute(select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id))
    resume = result.scalars().first()
    if not resume:
         raise HTTPException(404, "Resume not found")
    
    if not resume.extracted_text:
        raise HTTPException(400, "Resume has no text content")

    return await ai_manager.optimize_resume(db, current_user.id, resume.extracted_text, job_description)

@router.post("/match-job")
async def match_job(
    *,
    db: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
    resume_id: int = Body(..., embed=True),
    job_description: str = Body(..., embed=True),
) -> Dict[str, Any]:
    """
    Get a match score between resume and job description.
    """
    result = await db.execute(select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id))
    resume = result.scalars().first()
    if not resume:
         raise HTTPException(404, "Resume not found")

    # Construct simple profile for match
    profile = {
        "text": resume.extracted_text,
        "parsed": resume.parsed_data
    }
    
    return await ai_manager.match_job(db, current_user.id, profile, job_description)

@router.post("/generate-cover-letter")
async def generate_cover_letter(
    *,
    db: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
    resume_id: int = Body(..., embed=True),
    job_description: str = Body(..., embed=True),
) -> Dict[str, str]:
    result = await db.execute(select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id))
    resume = result.scalars().first()
    if not resume or not resume.extracted_text:
         raise HTTPException(404, "Resume not found or empty")

    profile = {"experience": resume.extracted_text[:2000]} # Truncate for safety
    letter = await ai_manager.generate_cover_letter(db, current_user.id, profile, job_description)
    return {"cover_letter": letter}
