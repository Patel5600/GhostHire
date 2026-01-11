from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    # Keep it human-sized. bcrypt wants <=72 BYTES.
    password: str = Field(min_length=6, max_length=72)


class UserRead(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
