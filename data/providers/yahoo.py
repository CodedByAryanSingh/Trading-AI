from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd
import yfinance as yf

from utils.logger import get_logger

logger = get_logger(__name__)


class YahooProvider:
    """Yahoo Finance provider wrapper for historical and live data."""

    def download_historical(
        self,
        ticker: str,
        interval: str = "1d",
        period: str = "1y",
        start: Optional[str] = None,
        end: Optional[str] = None,
        use_cache: bool = False,
    ) -> pd.DataFrame:
        interval = interval or "1d"
        period = period or "1y"

        kwargs: Dict[str, Any] = {
            "tickers": ticker,
            "interval": interval,
            "period": period,
            "progress": False,
        }

        if start is not None:
            kwargs["start"] = start
        if end is not None:
            kwargs["end"] = end

        data = yf.download(**kwargs)
        if data.empty:
            raise RuntimeError(f"No historical data returned for {ticker}")

        if data.index.tz is None:
            data.index = data.index.tz_localize("UTC")

        data = self._clean_missing(data)
        data.rename(columns={"Open": "Open", "High": "High", "Low": "Low", "Close": "Close", "Volume": "Volume"}, inplace=True)
        return data

    def get_live_price(self, ticker: str) -> float:
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.fast_info
        price = info.get("last_price") or info.get("regularMarketPrice") or info.get("previousClose")
        if price is None:
            history = ticker_obj.history(period="2d")
            if history.empty:
                raise RuntimeError(f"Unable to fetch live price for {ticker}")
            price = float(history["Close"].iloc[-1])
        return float(price)

    def _clean_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df = df.ffill().bfill()
        return df.dropna(how="all")
