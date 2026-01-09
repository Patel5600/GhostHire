from typing import Optional
from sqlmodel import SQLModel
from app.models.application import ApplicationBase
from app.schemas.job import JobRead

class ApplicationCreate(ApplicationBase):
    job_id: int

class ApplicationRead(ApplicationBase):
    id: int
    job_id: int
    user_id: int
    job: Optional[JobRead] = None
