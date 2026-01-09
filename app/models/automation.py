from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class ApplicationRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    job_id: int = Field(index=True)
    
    status: str = Field(default="pending") # pending, running, success, failed, captcha_detected
    screenshot_path: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Store simple log
    log_summary: Optional[str] = None

class AutomationLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="applicationrun.id")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str = "INFO"
    message: str
