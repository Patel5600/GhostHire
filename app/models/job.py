from typing import Optional, List, Dict
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, Column, JSON

# --- Enums & Shared ---

# --- Job Source Model ---
class JobSourceBase(SQLModel):
    name: str = Field(index=True, unique=True)
    type: str = Field(default="api") # 'api', 'scraper', 'rss'
    base_url: str
    config: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
    is_active: bool = Field(default=True)
    interval_minutes: int = Field(default=60)

class JobSource(JobSourceBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_run: Optional[datetime] = None
    
    jobs: List["Job"] = Relationship(back_populates="job_source")
    logs: List["IngestionLog"] = Relationship(back_populates="job_source")

# --- Ingestion Log Model ---
class IngestionLogBase(SQLModel):
    source_id: Optional[int] = Field(default=None, foreign_key="jobsource.id")
    status: str # 'success', 'failed', 'partial'
    jobs_found: int = 0
    jobs_ingested: int = 0
    jobs_deduplicated: int = 0
    error_message: Optional[str] = None
    duration_seconds: float = 0.0

class IngestionLog(IngestionLogBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    job_source: Optional[JobSource] = Relationship(back_populates="logs")

# --- Job Model ---
class JobBase(SQLModel):
    title: str
    company: str
    location: Optional[str] = None
    url: str = Field(unique=True, index=True)
    description: Optional[str] = None
    source: str = Field(default="manual") # Display name of source
    job_hash: str = Field(unique=True, index=True) # Unique ID (e.g. hash of title+company+loc)
    
    # Normalized Data
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: Optional[str] = None
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    is_remote: bool = Field(default=False)
    
    # Metadata
    posted_at: Optional[datetime] = None
    raw_data: Optional[Dict] = Field(default=None, sa_column=Column(JSON))

class Job(JobBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    source_id: Optional[int] = Field(default=None, foreign_key="jobsource.id")
    job_source: Optional[JobSource] = Relationship(back_populates="jobs")
    
    # Relationship to existing Application model (if any, forward ref string)
    applications: List["Application"] = Relationship(back_populates="job")
