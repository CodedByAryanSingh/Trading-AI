"""Market data endpoints."""
from __future__ import annotations
import datetime
from fastapi import APIRouter, HTTPException, Query, Response
from app.core.market_data import MarketDataService
from app.schemas import MarketOverviewResponse, OHLCVResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()
market_service = MarketDataService()

@router.get("/ohlcv", response_model=OHLCVResponse)
async def get_ohlcv(
    ticker: str = Query(..., min_length=1, max_length=20),
    interval: str = Query(default="1d"),
    period: str = Query(default="1y"),
):
    try:
        candles, volumes = await market_service.get_ohlcv(ticker, interval, period)
        return OHLCVResponse(candles=candles, volumes=volumes)
    except Exception as exc:
        logger.exception("Failed to fetch OHLCV for %s", ticker)
        raise HTTPException(status_code=500, detail=f"Failed to fetch market data: {exc}")

@router.get("/overview", response_model=MarketOverviewResponse)
async def market_overview(tickers: str = Query(default="AAPL,MSFT,GOOGL")):
    symbols = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    data = await market_service.get_overview(symbols)
    return MarketOverviewResponse(data=data)

@router.get("/export")
async def export_ohlcv(
    ticker: str = Query(..., min_length=1, max_length=20),
    interval: str = Query(default="1d"),
    period: str = Query(default="1y"),
    format: str = Query(default="csv", pattern="^(csv|parquet)$"),
):
    try:
        content, media_type, filename = await market_service.export_ohlcv(ticker, interval, period, format)
        return Response(content=content, media_type=media_type, headers={"Content-Disposition": f'attachment; filename="{filename}"'})
    except Exception as exc:
        logger.exception("Failed to export OHLCV for %s", ticker)
        raise HTTPException(status_code=500, detail=f"Failed to export market data: {exc}")

@router.get("/live-price")
async def live_price(ticker: str = Query(..., min_length=1, max_length=20)):
    try:
        price = await market_service.get_live_price(ticker)
        return {"ticker": ticker, "price": price, "timestamp": datetime.datetime.utcnow().isoformat()}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch live price")
