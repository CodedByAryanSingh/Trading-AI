"""SQLAlchemy database models."""
from __future__ import annotations
import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db import Base
if TYPE_CHECKING:
    from sqlalchemy.orm import Mapped

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    username: Mapped[str] = Column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = Column(String(100), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = Column(String(255), nullable=False)
    is_active: Mapped[bool] = Column(Boolean, default=True)
    created_at: Mapped[datetime.datetime] = Column(DateTime, default=datetime.datetime.utcnow)
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
    watchlists = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")

class Portfolio(Base):
    __tablename__ = "portfolios"
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = Column(String(100), default="Main")
    cash: Mapped[float] = Column(Float, default=100000.0)
    created_at: Mapped[datetime.datetime] = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User", back_populates="portfolios")

class Watchlist(Base):
    __tablename__ = "watchlists"
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = Column(String(100), default="Default")
    symbols: Mapped[str] = Column(Text, default="")
    created_at: Mapped[datetime.datetime] = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User", back_populates="watchlists")

class Trade(Base):
    __tablename__ = "trades"
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    ticker: Mapped[str] = Column(String(20), nullable=False)
    strategy: Mapped[str] = Column(String(50), nullable=False)
    side: Mapped[str] = Column(String(10), nullable=False)
    entry_price: Mapped[float] = Column(Float, nullable=False)
    exit_price: Mapped[float] = Column(Float, nullable=True)
    quantity: Mapped[int] = Column(Integer, default=1)
    pnl: Mapped[float] = Column(Float, nullable=True)
    entry_time: Mapped[datetime.datetime] = Column(DateTime, nullable=False)
    exit_time: Mapped[datetime.datetime] = Column(DateTime, nullable=True)
    created_at: Mapped[datetime.datetime] = Column(DateTime, default=datetime.datetime.utcnow)
