from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

class ApplicationStatus(str, Enum):
    SAVED = "saved"
    APPLYING = "applying" # In progress
    APPLIED = "applied"
    FAILED = "failed"
    INTERVIEWING = "interviewing"
    OFFER = "offer"
    REJECTED = "rejected"

class ApplicationBase(SQLModel):
    status: ApplicationStatus = Field(default=ApplicationStatus.SAVED)
    notes: Optional[str] = None

class Application(ApplicationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    job_id: int = Field(foreign_key="job.id")
    resume_id: Optional[int] = Field(default=None, foreign_key="resume.id")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="applications")
    job: "Job" = Relationship(back_populates="applications")
    logs: List["SubmissionLog"] = Relationship(back_populates="application")

class SubmissionLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="application.id")
    
    step: str # e.g. "contact_info", "upload_resume"
    status: str # "success", "error"
    message: Optional[str] = None
    screenshot_path: Optional[str] = None # Path to failure screenshot
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    application: Application = Relationship(back_populates="logs")
