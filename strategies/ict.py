"""ICT heuristic strategies (lightweight implementations).

These are simplified heuristics for ICT concepts such as OTE or daily bias.
They are intentionally conservative and meant to be extended by domain
experts. Kept unit-testable and side-effect free.
"""
from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from .base import Signal, Strategy, StrategyError
from indicators.technical import TechnicalIndicators
from utils.logger import get_logger

logger = get_logger(__name__)


class ICTStrategy(Strategy):
    """Basic ICT heuristics: daily bias using moving averages and OTE-like rule."""

    def __init__(self, data: pd.DataFrame, ote_window: int = 14, price_col: str = "Close") -> None:
        super().__init__(data)
        self.ote_window = int(ote_window)
        self.price_col = price_col
        self.ind = TechnicalIndicators(self.data)

    def generate(self) -> Signal:
        try:
            # daily bias via SMA(200)
            self.ind.add_sma(200, self.price_col)
            df = self.ind.data.dropna(subset=[self.price_col, "SMA_200"]) 
            last = df.iloc[-1]
            price = float(last[self.price_col])
            sma200 = float(last["SMA_200"])
            # bias
            if price > sma200:
                bias = "bullish"
            elif price < sma200:
                bias = "bearish"
            else:
                bias = "neutral"
            # OTE-like: measure retracement from recent swing high/low
            recent = df[self.price_col].dropna().iloc[-(self.ote_window + 1):-1]
            if len(recent) < 2:
                return Signal(signal="HOLD", confidence=0.0, details={"reason": "insufficient_data"})
            swing_high = float(recent.max())
            swing_low = float(recent.min())
            ote_level = swing_high - 0.618 * (swing_high - swing_low)
            details: Dict[str, Any] = {"bias": bias, "swing_high": swing_high, "swing_low": swing_low, "ote_level": ote_level}
            # signal rules (conservative): if price near OTE level and bias bullish -> BUY
            if bias == "bullish" and abs(price - ote_level) / (price if price != 0 else 1.0) < 0.02:
                return Signal(signal="BUY", confidence=0.6, details=details)
            if bias == "bearish" and abs(price - ote_level) / (price if price != 0 else 1.0) < 0.02:
                return Signal(signal="SELL", confidence=0.6, details=details)
            return Signal(signal="HOLD", confidence=0.0, details=details)
        except Exception as exc:
            logger.exception("ICTStrategy failed: %s", exc)
            raise StrategyError("ICTStrategy computation failed")
