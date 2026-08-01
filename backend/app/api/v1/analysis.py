"""Analysis and strategy endpoints."""
from __future__ import annotations
from typing import List
from fastapi import APIRouter, HTTPException
from app.core.data_loader import DataLoader
from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.strategies.manager import StrategyManager
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.post("/analyze", response_model=List[AnalyzeResponse])
async def analyze(req: AnalyzeRequest):
    loader = DataLoader()
    try:
        data_map = await loader.load_async(req.tickers, interval=req.interval, period=req.period)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to load market data")
    results = []
    for ticker, df in data_map.items():
        try:
            manager = StrategyManager(df)
            manager.auto_register_defaults(req.params or {})
            out = manager.aggregate()
            breakdown = [{"name": b["name"], "signal": b["signal"], "confidence": b["confidence"],
                          "score": 1 if b["signal"] == "BUY" else (-1 if b["signal"] == "SELL" else 0),
                          "details": b.get("details", {})} for b in out.get("breakdown", [])]
            results.append(AnalyzeResponse(ticker=ticker, signal=out["signal"],
                                           confidence=out["confidence"], score=out["score"], breakdown=breakdown))
        except Exception:
            logger.exception("Failed to analyze %s", ticker)
    return results

@router.post("/signals")
async def get_signals(tickers: List[str], interval: str = "1d", period: str = "1mo"):
    loader = DataLoader()
    data_map = await loader.load_async(tickers, interval=interval, period=period)
    results = {}
    for ticker, df in data_map.items():
        try:
            manager = StrategyManager(df)
            manager.auto_register_defaults()
            results[ticker] = manager.aggregate()
        except Exception:
            results[ticker] = {"error": "failed"}
    return results
