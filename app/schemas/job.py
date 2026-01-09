from typing import Optional
from sqlmodel import SQLModel
from app.models.job import JobBase

class JobCreate(JobBase):
    pass

class JobRead(JobBase):
    id: int
