"""
Pydantic schemas for the Trading-AI FastAPI endpoints.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    tickers: List[str] = Field(..., description="Tickers to analyze")
    period: Optional[str] = Field(None, description="Historical period alias, e.g., '1y'")
    interval: Optional[str] = Field(None, description="Data interval, e.g., '1d'")
    params: Optional[Dict[str, float]] = Field(None, description="Optional strategy params")


class IndicatorBreakdown(BaseModel):
    name: str
    signal: str
    score: int
    confidence: float


class AnalyzeResponse(BaseModel):
    ticker: str
    signal: str
    confidence: float
    score: float
    breakdown: Optional[List[IndicatorBreakdown]]


class PredictRequest(BaseModel):
    ticker: str
    horizon: Optional[str] = Field("1d", description="Prediction horizon")


class PredictResponse(BaseModel):
    ticker: str
    prediction: Dict[str, float]
    confidence: float
