from typing import Optional, Dict
from datetime import datetime
from sqlmodel import SQLModel, Field, JSON

class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    action: str # e.g., "delete_user", "stop_pipeline"
    target_resource: Optional[str] = None # e.g., "pipeline:123"
    details: Dict = Field(default={}, sa_type=JSON)
    ip_address: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SystemAlert(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    severity: str = "info" # info, warning, critical
    component: str # "scraper", "ai", "db"
    message: str
    is_resolved: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
