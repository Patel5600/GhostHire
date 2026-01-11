from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.schemas.token import Token

router = APIRouter()


@router.post("/login", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(deps.get_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    # OAuth form uses "username" for email. Don’t fight it.
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()

    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(
        subject=user.email,
        expires_delta=access_token_expires,
    )

    return {"access_token": token, "token_type": "bearer"}


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    *,
    db: AsyncSession = Depends(deps.get_session),
    user_in: UserCreate,
) -> Any:
    # Hard guards before touching crypto
    if not isinstance(user_in.password, str):
        raise HTTPException(status_code=400, detail="Password must be a string")

    if len(user_in.password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Password too long (max 72 bytes)")

    # Uniqueness check
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="User with this email already exists")

    # Hash only the password. Nothing else. Ever.
    try:
        hashed = security.get_password_hash(user_in.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    db_user = User(
        email=user_in.email,
        hashed_password=hashed,
        full_name=user_in.full_name,
        is_active=True,
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
