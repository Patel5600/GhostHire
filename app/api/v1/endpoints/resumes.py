from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime
import os
from pypdf import PdfReader

from app.api import deps
from app.models.resume import Resume
from app.services.resume_parser import parse_resume

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/")
async def upload_resume(
    *,
    db: AsyncSession = Depends(deps.get_session),
    file: UploadFile = File(...),
    current_user=Depends(deps.get_current_user),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save file
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Extract text from PDF
    reader = PdfReader(file_path)
    extracted_text = ""

    for page in reader.pages:
        extracted_text += page.extract_text() or ""

    # Parse resume into structured data
    parsed_data = parse_resume(extracted_text)

    # Save to DB
    resume = Resume(
        file_name=file.filename,
        file_path=file_path,
        extracted_text=extracted_text,
        parsed_data=parsed_data,
        user_id=current_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(resume)
    await db.commit()
    await db.refresh(resume)

    return {
        "id": resume.id,
        "file_name": resume.file_name,
        "parsed_data": parsed_data,
        "extracted_text": extracted_text[:500],  # preview only
        "created_at": resume.created_at,
    }
