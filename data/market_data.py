"""
Market data utilities.

Contains MarketData class capable of downloading historical data,
fetching live price, caching results, exporting to CSV/Parquet, cleaning
missing values, handling timezones, and simple retry logic.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import yfinance as yf

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MarketDataConfig:
    """Configuration for MarketData caching and defaults.

    Attributes:
        cache_dir: Directory where cached files are stored.
        default_interval: Default data interval for downloads.
        default_period: Default period for downloads when start/end not provided.
    """

    cache_dir: Path = Path("data/cache")
    default_interval: str = "1d"
    default_period: str = "1y"


class MarketData:
    """Market data helper class.

    This class wraps yfinance functionality and provides caching, retrying,
    cleaning, and export helpers. All public methods are unit-testable and
    handle errors gracefully while logging useful diagnostic information.
    """

    def __init__(self, config: Optional[MarketDataConfig] = None) -> None:
        """Initialize MarketData.

        Args:
            config: Optional MarketDataConfig, uses defaults when omitted.
        """
        self.config = config or MarketDataConfig()
        self.config.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, ticker: str, interval: str, start: Optional[str], end: Optional[str]) -> Path:
        """Return a cache path for a download request."""
        start_tag = start or "period"
        end_tag = end or "now"
        filename = f"{ticker}_{interval}_{start_tag}_{end_tag}.parquet"
        return self.config.cache_dir / filename

    def _retry(self, fn, attempts: int = 3, backoff: float = 1.0, *args, **kwargs):
        """Simple retry helper with exponential backoff.

        Args:
            fn: Callable to execute.
            attempts: Number of attempts.
            backoff: Initial backoff seconds (doubles each retry).
        """
        attempt = 0
        while attempt < attempts:
            try:
                return fn(*args, **kwargs)
            except Exception as exc:  # pragma: no cover - runtime retry safety
                attempt += 1
                logger.warning("Attempt %d/%d failed: %s", attempt, attempts, exc)
                if attempt >= attempts:
                    logger.exception("All retry attempts failed")
                    raise
                sleep = backoff * (2 ** (attempt - 1))
                time.sleep(sleep)

    def download_historical(
        self,
        ticker: str,
        interval: Optional[str] = None,
        period: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        use_cache: bool = True,
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """Download historical OHLCV data for a single ticker.

        Args:
            ticker: Ticker symbol (e.g., 'AAPL').
            interval: Data interval like '1d', '1h', '5m'.
            period: Period alias (e.g., '1y') used when start/end omitted.
            start: ISO date string for start date.
            end: ISO date string for end date.
            use_cache: Whether to read from cache if available.
            force_refresh: Force re-download and overwrite cache.

        Returns:
            DataFrame with OHLCV data indexed by timezone-aware DatetimeIndex.
        """
        interval = interval or self.config.default_interval
        period = period or self.config.default_period

        cache_path = self._cache_path(ticker, interval, start, end)
        if use_cache and cache_path.exists() and not force_refresh:
            logger.info("Loading %s from cache %s", ticker, cache_path)
            df = pd.read_parquet(cache_path)
            return df

        def _download():
            logger.info("Downloading %s (%s, %s..%s)", ticker, interval, start or period, end or "now")
            data = yf.download(tickers=ticker, interval=interval, period=period, start=start, end=end, progress=False)
            if data.empty:
                raise RuntimeError(f"No data returned for {ticker}")
            # Ensure tz-aware index
            if data.index.tz is None:
                data.index = data.index.tz_localize("UTC")
            return data

        df = self._retry(_download)

        # Basic cleaning
        df = self.clean_missing(df)

        # Save to cache
        try:
            df.to_parquet(cache_path)
            logger.info("Cached %s to %s", ticker, cache_path)
        except Exception:  # pragma: no cover - caching is best-effort
            logger.exception("Failed to cache data to %s", cache_path)

        return df

    def download_multiple(
        self,
        tickers: List[str],
        interval: Optional[str] = None,
        period: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        use_cache: bool = True,
        force_refresh: bool = False,
    ) -> Dict[str, pd.DataFrame]:
        """Download multiple tickers and return a mapping ticker -> DataFrame."""
        results: Dict[str, pd.DataFrame] = {}
        for t in tickers:
            try:
                results[t] = self.download_historical(t, interval, period, start, end, use_cache, force_refresh)
            except Exception:
                logger.exception("Failed to download %s", t)
        return results

    def get_live_price(self, ticker: str) -> float:
        """Return the latest live price for a ticker using yfinance fast_info.

        Args:
            ticker: Ticker symbol.

        Returns:
            Latest price as a float.
        """
        try:
            t = yf.Ticker(ticker)
            info = t.fast_info
            price = info.get("last_price") or info.get("last_close") or info.get("regularMarketPrice")
            if price is None:
                # fallback to historical last close
                df = t.history(period="2d")
                price = float(df["Close"].iloc[-1])
            return float(price)
        except Exception:  # pragma: no cover - runtime external call
            logger.exception("Failed to fetch live price for %s", ticker)
            raise

    def export_csv(self, df: pd.DataFrame, path: str) -> None:
        """Export DataFrame to CSV safely.

        Args:
            df: DataFrame to export.
            path: Path to CSV file.
        """
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(p)
        logger.info("Exported data to CSV: %s", p)

    def export_parquet(self, df: pd.DataFrame, path: str) -> None:
        """Export DataFrame to Parquet safely."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(p)
        logger.info("Exported data to Parquet: %s", p)

    def clean_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean missing values using forward-fill then back-fill.

        Args:
            df: Raw DataFrame possibly containing NaNs.

        Returns:
            DataFrame with NaNs filled where sensible.
        """
        df = df.copy()
        # common pattern: forward-fill prices then backfill remaining
        df = df.ffill().bfill()
        # drop rows that are still all NaN
        df = df.dropna(how="all")
        return df
