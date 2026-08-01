"""Authentication service layer."""
from __future__ import annotations
import datetime
from app.schemas import UserOut

class AuthService:
    @staticmethod
    async def authenticate_user(username: str, password: str) -> UserOut | None:
        return UserOut(id=1, username=username, email=f"{username}@trading-ai.com",
                       is_active=True, created_at=datetime.datetime.utcnow())
