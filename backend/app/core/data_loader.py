"""Async data loader wrapper."""
from __future__ import annotations
import asyncio
from typing import Dict, List
import pandas as pd
import yfinance as yf
from app.utils.logger import get_logger

logger = get_logger(__name__)

class DataLoader:
    async def load_async(self, tickers: List[str], interval: str = "1d", period: str = "1y") -> Dict[str, pd.DataFrame]:
        loop = asyncio.get_event_loop()
        tasks = [(t, loop.run_in_executor(None, self._load_single, t, interval, period)) for t in tickers]
        results = {}
        for ticker, task in tasks:
            try:
                df = await task
                if df is not None and not df.empty:
                    results[ticker] = df
            except Exception as exc:
                logger.error("Failed to load %s: %s", ticker, exc)
        return results

    def _load_single(self, ticker: str, interval: str, period: str) -> pd.DataFrame:
        df = yf.download(tickers=ticker, interval=interval, period=period, progress=False)
        if df.empty:
            raise ValueError(f"No data for {ticker}")
        if df.index.tz is None:
            df.index = df.index.tz_localize("UTC")
        return df
