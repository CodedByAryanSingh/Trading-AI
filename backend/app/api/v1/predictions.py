"""Prediction and ML endpoints."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.core.data_loader import DataLoader
from app.schemas import PredictRequest, PredictResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.post("/predict", response_model=PredictResponse)
async def predict(req: PredictRequest):
    try:
        loader = DataLoader()
        data_map = await loader.load_async([req.ticker], interval="1d", period="1mo")
        df = data_map.get(req.ticker)
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"No data for {req.ticker}")
        last_close = float(df["Close"].iloc[-1])
        prev_close = float(df["Close"].iloc[-2]) if len(df) > 1 else last_close
        momentum = (last_close - prev_close) / prev_close if prev_close > 0 else 0
        bullish_prob = min(0.9, max(0.1, 0.5 + momentum * 10))
        bearish_prob = 1.0 - bullish_prob
        confidence = abs(bullish_prob - 0.5) * 2
        prediction = "bullish" if bullish_prob > 0.6 else ("bearish" if bearish_prob > 0.6 else "neutral")
        return PredictResponse(ticker=req.ticker, prediction=prediction,
                               bullish_prob=round(bullish_prob, 4), bearish_prob=round(bearish_prob, 4),
                               confidence=round(confidence, 4))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Prediction failed")
