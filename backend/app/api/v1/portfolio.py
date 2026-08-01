"""Portfolio and watchlist endpoints."""
from __future__ import annotations
import datetime
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.dependencies import get_current_user
from app.schemas import PortfolioCreate, PortfolioOut, UserOut, WatchlistCreate, WatchlistOut

router = APIRouter()

@router.get("/portfolios", response_model=List[PortfolioOut])
async def get_portfolios(current_user: UserOut = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return [PortfolioOut(id=1, name="Main", cash=100000.0, created_at=datetime.datetime.utcnow())]

@router.post("/portfolios", response_model=PortfolioOut)
async def create_portfolio(payload: PortfolioCreate, current_user: UserOut = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return PortfolioOut(id=2, name=payload.name, cash=payload.cash, created_at=datetime.datetime.utcnow())

@router.get("/watchlists", response_model=List[WatchlistOut])
async def get_watchlists(current_user: UserOut = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return [WatchlistOut(id=1, name="Default", symbols=["AAPL", "MSFT", "GOOGL"], created_at=datetime.datetime.utcnow())]

@router.post("/watchlists", response_model=WatchlistOut)
async def create_watchlist(payload: WatchlistCreate, current_user: UserOut = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return WatchlistOut(id=2, name=payload.name,
                        symbols=payload.symbols.split(",") if payload.symbols else [],
                        created_at=datetime.datetime.utcnow())
