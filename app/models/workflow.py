from typing import Optional, List, Dict
from datetime import datetime
from sqlmodel import SQLModel, Field, JSON, Relationship

class WorkflowDefinition(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    steps: Dict = Field(default={}, sa_type=JSON) # List of steps e.g. ["scrape", "rank", "apply"]
    is_active: bool = True

class WorkflowRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    workflow_id: int = Field(foreign_key="workflowdefinition.id")
    user_id: int = Field(index=True)
    
    status: str = Field(default="pending") # pending, running, completed, failed
    current_step: Optional[str] = None
    
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class TaskRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    workflow_run_id: int = Field(foreign_key="workflowrun.id")
    task_name: str
    status: str = "pending"
    result_data: Optional[Dict] = Field(default=None, sa_type=JSON)
    created_at: datetime = Field(default_factory=datetime.utcnow)
