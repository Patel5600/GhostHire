from typing import Optional, Dict
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, Column, JSON

class MatchResultBase(SQLModel):
    score: float = Field(default=0.0)
    details: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
    model_version: str = "v1"
    feedback: Optional[str] = None # 'good', 'bad', etc.
    
    resume_id: int = Field(foreign_key="resume.id")
    job_id: int = Field(foreign_key="job.id")

class MatchResult(MatchResultBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships (Optional if you want to traverse back)
    # resume: "Resume" = Relationship()
    # job: "Job" = Relationship()
