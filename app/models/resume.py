from typing import Optional, Dict
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, JSON

class ResumeBase(SQLModel):
    file_name: str
    # In a real app with free tier, we might store text content here, 
    # and maybe the binary in a separate table or storage service.
    # For now, we will store extracted text to allow AI operations.
    extracted_text: Optional[str] = Field(default=None, sa_column_kwargs={"defer": True}) # Defer loading large text
    parsed_data: Optional[Dict] = Field(default={}, sa_type=JSON) 

class Resume(ResumeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    file_path: Optional[str] = None # Path if stored on disk/S3
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship(back_populates="resumes")
