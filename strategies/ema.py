"""EMA crossover strategy implementation."""
from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from .base import Signal, Strategy, StrategyError
from indicators.technical import TechnicalIndicators
from utils.logger import get_logger

logger = get_logger(__name__)


class EMAStrategy(Strategy):
    """Exponential Moving Average crossover strategy."""

    def __init__(self, data: pd.DataFrame, short: int = 12, long: int = 26, price_col: str = "Close") -> None:
        super().__init__(data)
        if short >= long:
            raise StrategyError("short period must be less than long period")
        self.short = int(short)
        self.long = int(long)
        self.price_col = price_col
        self.ind = TechnicalIndicators(self.data)

    def generate(self) -> Signal:
        try:
            self.ind.add_ema(self.short, self.price_col)
            self.ind.add_ema(self.long, self.price_col)
            df = self.ind.data.dropna(subset=[self.price_col, f"EMA_{self.short}", f"EMA_{self.long}"])
            last = df.iloc[-1]
            s = float(last[f"EMA_{self.short}"])
            l = float(last[f"EMA_{self.long}"])
            price = float(last[self.price_col])
            if s > l:
                signal = "BUY"
            elif s < l:
                signal = "SELL"
            else:
                signal = "HOLD"
            confidence = min(1.0, abs(s - l) / (price if price != 0 else 1.0))
            details: Dict[str, Any] = {"short": s, "long": l, "price": price}
            return Signal(signal=signal, confidence=float(confidence), details=details)
        except Exception as exc:
            logger.exception("EMAStrategy failed: %s", exc)
            raise StrategyError("EMAStrategy computation failed")
