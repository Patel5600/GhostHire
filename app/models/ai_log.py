from typing import Optional, Dict
from datetime import datetime
from sqlmodel import SQLModel, Field, JSON

class AIRequestLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    request_type: str = Field(index=True) # "optimization", "matching", "cover_letter"
    provider: str
    model: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    latency_ms: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Store minimal context to debug, avoid storing PII if possible in real logs, 
    # but for this specific "result" requirement we might link to results.

class AIResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    request_id: int = Field(foreign_key="airequestlog.id")
    content: Dict = Field(default={}, sa_type=JSON) # Structured response
    raw_response: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
