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
from app.schemas.user import UserCreate, UserRead, UserLogin
from app.schemas.token import Token

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(deps.get_session), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # 1. Fetch User
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()
    
    # 2. Authenticate
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    # 3. Create Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            subject=user.email, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=UserRead)
async def register_user(
    *,
    db: AsyncSession = Depends(deps.get_session),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalars().first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    
    # Create User
    db_user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
