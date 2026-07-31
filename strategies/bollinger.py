"""Bollinger Bands strategy implementation."""
from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from .base import Signal, Strategy, StrategyError
from indicators.technical import TechnicalIndicators
from utils.logger import get_logger

logger = get_logger(__name__)


class BollingerStrategy(Strategy):
    """Signals based on Bollinger Band extremes."""

    def __init__(self, data: pd.DataFrame, window: int = 20, n_std: float = 2.0, price_col: str = "Close") -> None:
        super().__init__(data)
        self.window = int(window)
        self.n_std = float(n_std)
        self.price_col = price_col
        self.ind = TechnicalIndicators(self.data)

    def generate(self) -> Signal:
        try:
            self.ind.add_bollinger(self.window, self.n_std, self.price_col)
            df = self.ind.data.dropna(subset=["BB_High", "BB_Low", "BB_Middle", self.price_col])
            last = df.iloc[-1]
            price = float(last[self.price_col])
            lower = float(last["BB_Low"])
            upper = float(last["BB_High"])
            if price < lower:
                signal = "BUY"
            elif price > upper:
                signal = "SELL"
            else:
                signal = "HOLD"
            if signal == "BUY":
                confidence = min(1.0, (lower - price) / (price if price != 0 else 1.0))
            elif signal == "SELL":
                confidence = min(1.0, (price - upper) / (price if price != 0 else 1.0))
            else:
                confidence = min(1.0, (upper - lower) / (price * 10 if price != 0 else 1.0))
            details: Dict[str, Any] = {"price": price, "lower": lower, "upper": upper}
            return Signal(signal=signal, confidence=float(abs(confidence)), details=details)
        except Exception as exc:
            logger.exception("BollingerStrategy failed: %s", exc)
            raise StrategyError("BollingerStrategy computation failed")
