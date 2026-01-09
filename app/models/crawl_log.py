from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class CrawlLogBase(SQLModel):
    source: str
    status: str # "success", "failed"
    jobs_found: int = 0
    jobs_ingested: int = 0
    error_message: Optional[str] = None

class CrawlLog(CrawlLogBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
