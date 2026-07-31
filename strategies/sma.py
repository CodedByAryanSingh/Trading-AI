"""SMA crossover strategy implementation."""
from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from .base import Signal, Strategy, StrategyError
from indicators.technical import TechnicalIndicators
from utils.logger import get_logger

logger = get_logger(__name__)


class SMAStrategy(Strategy):
    """Simple SMA crossover strategy.

    Signals:
        - BUY when short SMA crosses above long SMA
        - SELL when short SMA crosses below long SMA
        - HOLD otherwise
    """

    def __init__(self, data: pd.DataFrame, short: int = 50, long: int = 200, price_col: str = "Close") -> None:
        super().__init__(data)
        if short >= long:
            raise StrategyError("short period must be less than long period")
        self.short = int(short)
        self.long = int(long)
        self.price_col = price_col
        self.ind = TechnicalIndicators(self.data)

    def generate(self) -> Signal:
        """Compute SMA crossover signal for the latest bar."""
        try:
            self.ind.add_sma(self.short, self.price_col)
            self.ind.add_sma(self.long, self.price_col)
            df = self.ind.data.dropna(subset=[self.price_col, f"SMA_{self.short}", f"SMA_{self.long}"])
            last = df.iloc[-1]
            s = float(last[f"SMA_{self.short}"])
            l = float(last[f"SMA_{self.long}"])
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
            logger.exception("SMAStrategy failed: %s", exc)
            raise StrategyError("SMAStrategy computation failed")
