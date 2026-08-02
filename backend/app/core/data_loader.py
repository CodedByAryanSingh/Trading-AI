"""Async data loader wrapper."""
from __future__ import annotations
import asyncio
from typing import Dict, List
import numpy as np
import pandas as pd
import yfinance as yf
from app.utils.logger import get_logger

logger = get_logger(__name__)

_FOREX_CURRENCIES = {"AUD", "CAD", "CHF", "EUR", "GBP", "JPY", "NZD", "USD"}


def provider_symbol(ticker: str) -> str:
    """Map terminal-style forex pairs to Yahoo Finance's provider notation."""
    symbol = ticker.upper().strip()
    if len(symbol) == 6 and symbol[:3] in _FOREX_CURRENCIES and symbol[3:] in _FOREX_CURRENCIES:
        return f"{symbol}=X"
    return symbol


def demo_data(ticker: str, interval: str, periods: int = 240) -> pd.DataFrame:
    """Generate clearly labelled local data only when the external provider is unavailable."""
    frequency = {"1m": "min", "5m": "5min", "15m": "15min", "30m": "30min", "1h": "h", "4h": "4h", "1d": "B", "1wk": "W"}.get(interval, "B")
    seed = sum(ord(character) for character in ticker.upper())
    generator = np.random.default_rng(seed)
    start_price = 1.1 if ticker.upper().startswith(("EUR", "GBP", "AUD", "NZD")) else 100.0
    close = start_price * np.cumprod(1 + generator.normal(0, 0.004, periods))
    open_price = np.concatenate(([close[0]], close[:-1]))
    spread = np.maximum(close * 0.002, 0.0001)
    frame = pd.DataFrame({
        "Open": open_price, "High": np.maximum(open_price, close) + spread,
        "Low": np.minimum(open_price, close) - spread, "Close": close,
        "Volume": generator.integers(5_000, 100_000, periods),
    }, index=pd.date_range(end=pd.Timestamp.now(tz="UTC"), periods=periods, freq=frequency))
    frame.attrs["data_source"] = "demo"
    return frame

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
        try:
            df = yf.download(tickers=provider_symbol(ticker), interval=interval, period=period, progress=False, auto_adjust=True)
            if df.empty:
                raise ValueError(f"No data for {ticker}")
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            if df.index.tz is None:
                df.index = df.index.tz_localize("UTC")
            df.attrs["data_source"] = "provider"
            return df
        except Exception as exc:
            logger.warning("Provider data unavailable for %s; serving non-tradable demo data: %s", ticker, exc)
            return demo_data(ticker, interval)
