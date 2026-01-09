from typing import List, Any
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import ResumeRead
from app.services.resume_parser import parse_pdf_content

router = APIRouter()

@router.post("/", response_model=ResumeRead)
async def upload_resume(
    *,
    db: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
    file: UploadFile = File(...)
) -> Any:
    """
    Upload a resume (PDF), extract text, and save to DB.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported")
    
    # Extract Text
    text_content = await parse_pdf_content(file)
    
    # Save to DB
    # Note: In a real app, save 'file' to S3/Supabase Storage and store path in file_path
    resume = Resume(
        user_id=current_user.id,
        file_name=file.filename,
        extracted_text=text_content,
        file_path=f"uploads/{current_user.id}/{file.filename}" # Placeholder path
    )
    
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    return resume

@router.get("/", response_model=List[ResumeRead])
async def read_resumes(
    db: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve resumes.
    """
    result = await db.execute(
        select(Resume).where(Resume.user_id == current_user.id).offset(skip).limit(limit)
    )
    resumes = result.scalars().all()
    return resumes

@router.delete("/{id}", response_model=ResumeRead)
async def delete_resume(
    *,
    db: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
    id: int,
) -> Any:
    """
    Delete a resume.
    """
    result = await db.execute(
        select(Resume).where(Resume.id == id, Resume.user_id == current_user.id)
    )
    resume = result.scalars().first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    await db.delete(resume)
    await db.commit()
    return resume
