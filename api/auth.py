"""Authentication routes for Trading-AI using peewee and JWT.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
import datetime

from passlib.context import CryptContext
from jose import jwt

from api.db import init_db, User
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Initialize DB (idempotent)
init_db()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = "CHANGE_ME_TO_A_SECURE_VALUE"
JWT_ALGORITHM = "HS256"
JWT_EXPIRES_MINUTES = 60 * 24 * 7

class RegisterIn(BaseModel):
    username: str
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + (expires_delta or datetime.timedelta(minutes=JWT_EXPIRES_MINUTES))
    to_encode.update({"exp": expire})
    encoded = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded


@router.post("/register", response_model=TokenOut)
async def register(payload: RegisterIn):
    # basic uniqueness checks
    existing = User.select().where((User.username == payload.username) | (User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with that username or email already exists")
    pwd = hash_password(payload.password)
    user = User.create(username=payload.username, email=payload.email, password_hash=pwd)
    token = create_token({"sub": str(user.id), "username": user.username})
    return {"access_token": token}


class LoginIn(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    password: str


@router.post("/login", response_model=TokenOut)
async def login(payload: LoginIn):
    if payload.username:
        user = User.select().where(User.username == payload.username).first()
    elif payload.email:
        user = User.select().where(User.email == payload.email).first()
    else:
        raise HTTPException(status_code=400, detail="username or email required")
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"sub": str(user.id), "username": user.username})
    return {"access_token": token}
