from enum import Enum
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"
    SUPPORT = "support"

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    full_name: Optional[str] = None
    is_active: bool = True
    role: UserRole = Field(default=UserRole.USER)

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    resumes: List["Resume"] = Relationship(back_populates="user")
    applications: List["Application"] = Relationship(back_populates="user")
