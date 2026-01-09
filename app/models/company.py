from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class CompanyBase(SQLModel):
    name: str = Field(index=True, unique=True)
    domain: Optional[str] = None
    careers_page_url: Optional[str] = None
    logo_url: Optional[str] = None

class Company(CompanyBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # We will soft-link jobs by matching string for now to avoid breaking existing Job schema significantly, 
    # but ideally this would be a relationship.
