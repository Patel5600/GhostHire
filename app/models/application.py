from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

class ApplicationStatus(str, Enum):
    SAVED = "saved"
    APPLIED = "applied"
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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship(back_populates="applications")
    job: "Job" = Relationship(back_populates="applications")
