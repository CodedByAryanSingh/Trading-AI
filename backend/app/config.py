"""Application configuration using Pydantic Settings."""
from __future__ import annotations
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Trading-AI API"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, alias="DEBUG")
    database_url: str = Field(default="sqlite+aiosqlite:///data/trading_ai.db", alias="DATABASE_URL")
    jwt_secret: str = Field(default="change-me-in-production", alias="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60 * 24 * 7
    cors_origins: str = Field(default="http://localhost:5173,http://127.0.0.1:5173", alias="CORS_ORIGINS")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    mt5_enabled: bool = Field(default=True, alias="MT5_ENABLED")
    mt5_path: str | None = Field(default=None, alias="MT5_PATH")
    mt5_login: int | None = Field(default=None, alias="MT5_LOGIN")
    mt5_password: str | None = Field(default=None, alias="MT5_PASSWORD")
    mt5_server: str | None = Field(default=None, alias="MT5_SERVER")

    @property
    def cors_origin_list(self) -> List[str]:
        configured = [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
        return list(dict.fromkeys(["http://localhost:5173", "http://127.0.0.1:5173", *configured]))


settings = Settings()
