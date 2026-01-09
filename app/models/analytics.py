from typing import Optional, List, Dict
from datetime import datetime
from sqlmodel import SQLModel, Field, JSON

class ApplicationOutcome(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    application_id: int = Field(index=True)
    job_id: int
    user_id: int
    
    # Outcome tracking
    outcome_status: str = Field(index=True) # applied, interview, offer, rejected, ghosted
    response_time_days: Optional[float] = None
    
    # Snapshot of data at time of application for correlation
    resume_version_id: Optional[int] = None
    cover_letter_sentiment_score: Optional[float] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DailyMetric(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime = Field(index=True)
    user_id: int = Field(index=True)
    
    applications_sent: int = 0
    interviews_received: int = 0
    rejections_received: int = 0
    
    # Store aggregated insights JSON
    skill_gaps: Dict = Field(default={}, sa_type=JSON) 
    top_performing_keywords: Dict = Field(default={}, sa_type=JSON)

class OptimizationSuggestion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    category: str = Field(index=True) # resume, timing, skill
    suggestion: str
    confidence_score: float = 0.0
    is_applied: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
