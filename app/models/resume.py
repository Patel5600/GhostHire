from typing import Optional, Dict
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, JSON

class ResumeBase(SQLModel):
    file_name: str

    # Store extracted text normally. If you want to defer loading,
    # do it at query time, not in schema.
    extracted_text: Optional[str] = Field(default=None)

    parsed_data: Optional[Dict] = Field(default=None, sa_type=JSON)

class Resume(ResumeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    file_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship(back_populates="resumes")
