"""RSI-based mean-reversion strategy."""
from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from .base import Signal, Strategy, StrategyError
from indicators.technical import TechnicalIndicators
from utils.logger import get_logger

logger = get_logger(__name__)


class RSIStrategy(Strategy):
    """RSI strategy that signals on overbought/oversold conditions."""

    def __init__(self, data: pd.DataFrame, window: int = 14, lower: int = 30, upper: int = 70, price_col: str = "Close") -> None:
        super().__init__(data)
        self.window = int(window)
        self.lower = int(lower)
        self.upper = int(upper)
        self.price_col = price_col
        self.ind = TechnicalIndicators(self.data)

    def generate(self) -> Signal:
        try:
            self.ind.add_rsi(self.window, self.price_col)
            df = self.ind.data.dropna(subset=[f"RSI_{self.window}"])
            last = df.iloc[-1]
            rsi = float(last[f"RSI_{self.window}"])
            if rsi < self.lower:
                signal = "BUY"
            elif rsi > self.upper:
                signal = "SELL"
            else:
                signal = "HOLD"
            if signal == "BUY":
                confidence = min(1.0, (self.lower - rsi) / (self.lower if self.lower != 0 else 1.0))
            elif signal == "SELL":
                confidence = min(1.0, (rsi - self.upper) / (100 - self.upper if (100 - self.upper) != 0 else 1.0))
            else:
                confidence = 0.0
            details: Dict[str, Any] = {"rsi": rsi}
            return Signal(signal=signal, confidence=float(confidence), details=details)
        except Exception as exc:
            logger.exception("RSIStrategy failed: %s", exc)
            raise StrategyError("RSIStrategy computation failed")
