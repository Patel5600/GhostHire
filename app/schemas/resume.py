from typing import Optional, Dict
from datetime import datetime
from sqlmodel import SQLModel

class ResumeCreate(SQLModel):
    # File upload validation might happen at controller level
    pass

class ResumeRead(SQLModel):
    id: int
    file_name: str
    parsed_data: Optional[Dict] = None
    created_at: datetime
    updated_at: datetime
