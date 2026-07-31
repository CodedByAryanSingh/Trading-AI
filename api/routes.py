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


@router.get('/ohlcv')
async def get_ohlcv(ticker: str, interval: str = '1d', period: str = '1mo', start: str | None = None, end: str | None = None):
    """Return OHLCV data for a single ticker formatted for the frontend chart.

    Query parameters:
    - ticker: ticker symbol (required)
    - interval: data granularity (1d, 1h, 1m, etc.)
    - period: period alias (e.g., 1mo, 3mo, 1y) used when start/end omitted
    - start, end: ISO dates to define an explicit range (optional)
    """
    dl = DataLoader()
    try:
        data_map = dl.load([ticker], interval=interval, period=period)
        df = data_map.get(ticker)
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"No data for {ticker}")

        # Format data for lightweight-charts: time must be YYYY-MM-DD or unix timestamp
        candles = []
        volumes = []
        # decide whether to return unix timestamps (seconds) for intraday intervals
        use_unix = False
        if any(x in interval for x in ['m', 'h']):
            use_unix = True

        for idx, row in df.iterrows():
            # idx may be tz-aware Timestamp
            t = idx.to_pydatetime()
            if use_unix:
                # lightweight-charts expects unix seconds for numeric times
                time_val = int(t.timestamp())
            else:
                time_val = t.strftime('%Y-%m-%d')

            candles.append({
                'time': time_val,
                'open': float(row.get('Open', 0.0)),
                'high': float(row.get('High', 0.0)),
                'low': float(row.get('Low', 0.0)),
                'close': float(row.get('Close', 0.0)),
            })
            volumes.append({
                'time': time_val,
                'value': float(row.get('Volume', 0.0)),
            })

        return {'candles': candles, 'volumes': volumes}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception('Failed to fetch OHLCV for %s: %s', ticker, exc)
        raise HTTPException(status_code=500, detail='Failed to fetch OHLCV data')
