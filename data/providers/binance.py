from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import requests

from utils.logger import get_logger

logger = get_logger(__name__)


class BinanceProvider:
    """Binance market data provider for crypto symbols.

    This provider uses Binance public REST endpoints to fetch live prices and
    historical candlestick data. It is designed to be lightweight and
    dependency-free beyond requests and pandas.
    """

    BASE_URL = "https://api.binance.com/api/v3"
    INTERVAL_MAP = {
        "1m": "1m",
        "3m": "3m",
        "5m": "5m",
        "15m": "15m",
        "30m": "30m",
        "1h": "1h",
        "2h": "2h",
        "4h": "4h",
        "6h": "6h",
        "8h": "8h",
        "12h": "12h",
        "1d": "1d",
        "3d": "3d",
        "1w": "1w",
        "1M": "1M",
    }

    def __init__(self, session: Optional[requests.Session] = None) -> None:
        self.session = session or requests.Session()

    def _request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{endpoint}"
        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    def normalize_symbol(self, ticker: str) -> str:
        symbol = ticker.upper().replace("-", "").replace("/", "")
        if symbol.endswith("USD") and not symbol.endswith("USDT"):
            symbol = f"{symbol[:-3]}USDT"
        return symbol

    def get_live_price(self, ticker: str) -> float:
        symbol = self.normalize_symbol(ticker)
        payload = self._request("ticker/price", {"symbol": symbol})
        return float(payload["price"])

    def get_historical_ohlcv(
        self,
        ticker: str,
        interval: str = "1d",
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 500,
    ) -> pd.DataFrame:
        symbol = self.normalize_symbol(ticker)
        interval = self.INTERVAL_MAP.get(interval, interval)
        params: Dict[str, Any] = {"symbol": symbol, "interval": interval, "limit": limit}

        if start is not None:
            params["startTime"] = int(datetime.fromisoformat(start).timestamp() * 1000)
        if end is not None:
            params["endTime"] = int(datetime.fromisoformat(end).timestamp() * 1000)

        raw = self._request("klines", params)
        if not raw:
            raise RuntimeError(f"No historical data returned for {ticker}")

        columns = [
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume",
            "ignore",
        ]
        df = pd.DataFrame(raw, columns=columns)
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
        df = df.set_index("open_time")
        df = df[["open", "high", "low", "close", "volume"]].astype(float)
        df.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume"}, inplace=True)
        return df
