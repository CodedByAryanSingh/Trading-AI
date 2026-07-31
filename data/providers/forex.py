from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional, Tuple

import pandas as pd
import requests

from utils.logger import get_logger

logger = get_logger(__name__)


class ForexProvider:
    """Forex market data provider using exchangerate.host."""

    BASE_URL = "https://api.exchangerate.host"

    def __init__(self, session: Optional[requests.Session] = None) -> None:
        self.session = session or requests.Session()

    def _parse_pair(self, ticker: str) -> Tuple[str, str]:
        symbol = ticker.upper().replace(" ", "").replace("/", "")
        if len(symbol) == 6:
            return symbol[:3], symbol[3:]
        if "USD" in symbol and len(symbol) == 7:
            return symbol[:3], symbol[4:]
        raise ValueError(f"Unable to parse forex ticker '{ticker}'")

    def get_live_rate(self, ticker: str) -> float:
        base, quote = self._parse_pair(ticker)
        response = self.session.get(
            f"{self.BASE_URL}/latest",
            params={"base": base, "symbols": quote},
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
        if not payload.get("success"):
            raise RuntimeError(f"Forex provider error: {payload}")
        rate = payload["rates"].get(quote)
        if rate is None:
            raise RuntimeError(f"No forex rate returned for {ticker}")
        return float(rate)

    def download_historical(
        self,
        ticker: str,
        start: str,
        end: str,
        interval: str = "1d",
    ) -> pd.DataFrame:
        if interval != "1d":
            raise ValueError("Forex provider currently supports daily data only")

        base, quote = self._parse_pair(ticker)
        response = self.session.get(
            f"{self.BASE_URL}/timeseries",
            params={"base": base, "symbols": quote, "start_date": start, "end_date": end, "places": 6},
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()
        if not payload.get("success"):
            raise RuntimeError(f"Forex provider error: {payload}")

        rates = payload.get("rates", {})
        if not rates:
            raise RuntimeError(f"No historical forex data returned for {ticker}")

        data = [
            {
                "date": pd.to_datetime(date, utc=True),
                "Open": float(rate[quote]),
                "High": float(rate[quote]),
                "Low": float(rate[quote]),
                "Close": float(rate[quote]),
                "Volume": 0.0,
            }
            for date, rate in sorted(rates.items())
        ]

        df = pd.DataFrame(data).set_index("date")
        return df
