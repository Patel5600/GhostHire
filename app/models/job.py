from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class JobBase(SQLModel):
    title: str
    company: str
    location: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = Field(default="manual") # e.g., 'linkedin', 'manual'
    job_hash: Optional[str] = Field(default=None, index=True) # unique hash of url/content to prevent dupes

class Job(JobBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    applications: List["Application"] = Relationship(back_populates="job")
