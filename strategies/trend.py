"""Simple trend-following strategy using moving average slope."""
from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from .base import Signal, Strategy, StrategyError
from indicators.technical import TechnicalIndicators
from utils.logger import get_logger

logger = get_logger(__name__)


class TrendStrategy(Strategy):
    """Trend following via SMA slope comparison.

    Uses short and long SMA slope to determine trend strength.
    """

    def __init__(self, data: pd.DataFrame, short: int = 50, long: int = 200, price_col: str = "Close") -> None:
        super().__init__(data)
        if short >= long:
            raise StrategyError("short period must be less than long period")
        self.short = int(short)
        self.long = int(long)
        self.price_col = price_col
        self.ind = TechnicalIndicators(self.data)

    def _slope(self, series: pd.Series, length: int = 3) -> float:
        # simple slope estimate over `length` bars
        recent = series.dropna().iloc[-length:]
        if len(recent) < 2:
            return 0.0
        return float((recent.iloc[-1] - recent.iloc[0]) / max(1, len(recent) - 1))

    def generate(self) -> Signal:
        try:
            self.ind.add_sma(self.short, self.price_col)
            self.ind.add_sma(self.long, self.price_col)
            df = self.ind.data.dropna(subset=[f"SMA_{self.short}", f"SMA_{self.long}", self.price_col])
            last = df.iloc[-1]
            s = df[f"SMA_{self.short}"]
            l = df[f"SMA_{self.long}"]
            slope_short = self._slope(s)
            slope_long = self._slope(l)
            # bullish when short slope > long slope and both positive
            if slope_short > slope_long and slope_short > 0:
                signal = "BUY"
            elif slope_short < slope_long and slope_short < 0:
                signal = "SELL"
            else:
                signal = "HOLD"
            # confidence derived from difference in slopes normalized by price
            price = float(last[self.price_col])
            conf_raw = abs(slope_short - slope_long) / (price if price != 0 else 1.0)
            confidence = min(1.0, conf_raw)
            details: Dict[str, Any] = {"slope_short": slope_short, "slope_long": slope_long}
            return Signal(signal=signal, confidence=float(confidence), details=details)
        except Exception as exc:
            logger.exception("TrendStrategy failed: %s", exc)
            raise StrategyError("TrendStrategy computation failed")
