"""Pydantic schemas for API requests and responses."""
from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

# Auth
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

# Market
class OHLCVRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=20)
    interval: str = Field(default="1d", pattern="^(1m|5m|15m|30m|1h|4h|1d|1wk|1mo)$")
    period: str = Field(default="1y", pattern="^(1d|5d|1mo|3mo|6mo|1y|2y|5y|10y|ytd|max)$")

class Candle(BaseModel):
    time: int | str
    open: float
    high: float
    low: float
    close: float

class Volume(BaseModel):
    time: int | str
    value: float

class OHLCVResponse(BaseModel):
    candles: List[Candle]
    volumes: List[Volume]

class MarketOverviewItem(BaseModel):
    ticker: str
    price: Optional[float]
    change: Optional[float]
    change_percent: Optional[float]

class MarketOverviewResponse(BaseModel):
    data: List[MarketOverviewItem]

# Analysis
class AnalyzeRequest(BaseModel):
    tickers: List[str] = Field(..., min_length=1, max_length=20)
    interval: str = Field(default="1d", pattern="^(1d|1h|1wk)$")
    period: str = Field(default="1y")
    params: Optional[Dict[str, float]] = Field(default=None)

class IndicatorBreakdown(BaseModel):
    name: str
    signal: str
    confidence: float
    score: int
    details: Dict[str, Any]

class AnalyzeResponse(BaseModel):
    ticker: str
    signal: str
    confidence: float
    score: float
    breakdown: List[IndicatorBreakdown]

# Predictions
class PredictRequest(BaseModel):
    ticker: str
    horizon: str = Field(default="1d", pattern="^(1d|5d|1mo)$")

class PredictResponse(BaseModel):
    ticker: str
    prediction: str
    bullish_prob: float = Field(..., ge=0.0, le=1.0)
    bearish_prob: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)

# Backtest
class BacktestRequest(BaseModel):
    ticker: str
    strategy: str = Field(default="sma", pattern="^(sma|ema|rsi|macd|bollinger|trend|breakout|smc|ict)$")
    period: str = Field(default="6mo")
    initial_cash: float = Field(default=100000.0, gt=0)

class TradeRecord(BaseModel):
    entry_time: str
    exit_time: Optional[str]
    side: str
    entry_price: float
    exit_price: Optional[float]
    pnl: Optional[float]

class BacktestResponse(BaseModel):
    summary: Dict[str, float]
    trades: List[TradeRecord]
    equity: List[Dict[str, float]]

# Portfolio
class PortfolioCreate(BaseModel):
    name: str = Field(default="Main", max_length=100)
    cash: float = Field(default=100000.0, gt=0)

class PortfolioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    cash: float
    created_at: datetime

class WatchlistCreate(BaseModel):
    name: str = Field(default="Default", max_length=100)
    symbols: str = Field(default="")

class WatchlistOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    symbols: List[str]
    created_at: datetime
