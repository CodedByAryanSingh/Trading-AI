"""Market data service with caching and retry logic."""
from __future__ import annotations
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import yfinance as yf
from app.utils.logger import get_logger

logger = get_logger(__name__)

class MarketDataService:
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, ticker: str, interval: str, period: str) -> Path:
        return self.cache_dir / f"{ticker}_{interval}_{period}.parquet"

    async def get_ohlcv(self, ticker: str, interval: str = "1d", period: str = "1y") -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        cache_path = self._cache_path(ticker, interval, period)
        df = None
        if cache_path.exists():
            try:
                df = pd.read_parquet(cache_path)
            except Exception:
                df = None
        if df is None:
            df = yf.download(tickers=ticker, interval=interval, period=period, progress=False)
            if df.empty:
                raise ValueError(f"No data returned for {ticker}")
            if df.index.tz is None:
                df.index = df.index.tz_localize("UTC")
            try:
                df.to_parquet(cache_path)
            except Exception as exc:
                logger.warning("Failed to cache data: %s", exc)
        use_unix = any(x in interval for x in ["m", "h"])
        candles, volumes = [], []
        for idx, row in df.iterrows():
            t = idx.to_pydatetime()
            time_val = int(t.timestamp()) if use_unix else t.strftime("%Y-%m-%d")
            candles.append({"time": time_val, "open": float(row.get("Open", 0)),
                            "high": float(row.get("High", 0)), "low": float(row.get("Low", 0)),
                            "close": float(row.get("Close", 0))})
            volumes.append({"time": time_val, "value": float(row.get("Volume", 0))})
        return candles, volumes

    async def get_overview(self, symbols: List[str]) -> List[Dict[str, Any]]:
        results = []
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                current_price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
                previous_close = info.get("previousClose") or info.get("regularMarketPreviousClose") or current_price
                change = current_price - previous_close if current_price and previous_close else 0
                change_percent = (change / previous_close * 100) if previous_close else 0
                results.append({"ticker": symbol, "price": round(current_price, 2) if current_price else None,
                                 "change": round(change, 2) if current_price else None,
                                 "change_percent": round(change_percent, 2) if current_price else None})
            except Exception as exc:
                logger.warning("Failed to get overview for %s: %s", symbol, exc)
                results.append({"ticker": symbol, "price": None, "change": None, "change_percent": None})
        return results

    async def get_live_price(self, ticker: str) -> float:
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info
        price = info.get("currentPrice") or info.get("regularMarketPrice")
        if price is None:
            raise ValueError(f"Could not fetch price for {ticker}")
        return float(price)
