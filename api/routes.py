"""
API routes for Trading-AI.

Defines a small set of endpoints for analysis and prediction that call into
the core DataLoader and StrategyEngine.
"""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException

from api.schemas import AnalyzeRequest, AnalyzeResponse
from data.data_loader import DataLoader
from strategies.strategy import StrategyEngine
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/analyze", response_model=List[AnalyzeResponse])
async def analyze(req: AnalyzeRequest):
    """Analyze tickers and return signals using the strategy engine."""
    dl = DataLoader()
    try:
        data_map = dl.load(req.tickers, interval=req.interval or "1d", period=req.period or "1y")
    except Exception as exc:
        logger.exception("Failed to load data: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to load market data")

    results = []
    for ticker, df in data_map.items():
        try:
            engine = StrategyEngine(df)
            out = engine.multi_indicator_confirmation(req.params or {})
            results.append(AnalyzeResponse(ticker=ticker, signal=out["signal"], confidence=out["confidence"], score=out["score"], breakdown=out.get("breakdown")))
        except Exception:
            logger.exception("Failed to analyze %s", ticker)
            # skip ticker on error
            continue

    return results
