"""Authentication endpoints."""
from __future__ import annotations
import datetime
from datetime import timedelta
from fastapi import APIRouter, Depends
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.db import get_db
from app.schemas import TokenResponse, UserLogin, UserOut, UserRegister
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + (expires_delta or timedelta(minutes=settings.jwt_expires_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)

@router.post("/register", response_model=TokenResponse)
async def register(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    logger.info("New user registration: %s", payload.username)
    return TokenResponse(access_token=create_access_token({"sub": payload.username}))

@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    logger.info("User login attempt: %s", payload.username)
    return TokenResponse(access_token=create_access_token({"sub": payload.username}))

@router.get("/me", response_model=UserOut)
async def get_me():
    return UserOut(id=1, username="demo", email="demo@trading-ai.com",
                   is_active=True, created_at=datetime.datetime.utcnow())
