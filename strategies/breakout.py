"""Breakout strategy: price breaks above recent high or below recent low."""
from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from .base import Signal, Strategy, StrategyError
from utils.logger import get_logger

logger = get_logger(__name__)


class BreakoutStrategy(Strategy):
    """Detects simple range breakouts over a lookback window."""

    def __init__(self, data: pd.DataFrame, lookback: int = 20, price_col: str = "Close") -> None:
        super().__init__(data)
        self.lookback = int(lookback)
        self.price_col = price_col

    def generate(self) -> Signal:
        try:
            df = self.data.dropna(subset=[self.price_col, "High", "Low"]) 
            if len(df) < self.lookback + 1:
                return Signal(signal="HOLD", confidence=0.0, details={"reason": "insufficient_data"})
            recent = df.iloc[-(self.lookback + 1):-1]
            high = float(recent["High"].max())
            low = float(recent["Low"].min())
            last = df.iloc[-1]
            price = float(last[self.price_col])
            if price > high:
                signal = "BUY"
                confidence = min(1.0, (price - high) / (price if price != 0 else 1.0))
            elif price < low:
                signal = "SELL"
                confidence = min(1.0, (low - price) / (price if price != 0 else 1.0))
            else:
                signal = "HOLD"
                confidence = 0.0
            details: Dict[str, Any] = {"range_high": high, "range_low": low, "price": price}
            return Signal(signal=signal, confidence=float(confidence), details=details)
        except Exception as exc:
            logger.exception("BreakoutStrategy failed: %s", exc)
            raise StrategyError("BreakoutStrategy computation failed")
