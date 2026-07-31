"""MACD momentum strategy."""
from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from .base import Signal, Strategy, StrategyError
from indicators.technical import TechnicalIndicators
from utils.logger import get_logger

logger = get_logger(__name__)


class MACDStrategy(Strategy):
    """MACD crossover strategy using MACD line and signal line."""

    def __init__(self, data: pd.DataFrame, price_col: str = "Close") -> None:
        super().__init__(data)
        self.price_col = price_col
        self.ind = TechnicalIndicators(self.data)

    def generate(self) -> Signal:
        try:
            self.ind.add_macd(self.price_col)
            df = self.ind.data.dropna(subset=["MACD", "MACD_Signal", "MACD_Histogram"])
            last = df.iloc[-1]
            macd = float(last["MACD"])
            macd_sig = float(last["MACD_Signal"])
            hist = float(last.get("MACD_Histogram", 0.0))
            if macd > macd_sig:
                signal = "BUY"
            elif macd < macd_sig:
                signal = "SELL"
            else:
                signal = "HOLD"
            price = float(last[self.price_col])
            confidence = min(1.0, abs(hist) / (price if price != 0 else 1.0))
            details: Dict[str, Any] = {"macd": macd, "signal_line": macd_sig, "hist": hist}
            return Signal(signal=signal, confidence=float(confidence), details=details)
        except Exception as exc:
            logger.exception("MACDStrategy failed: %s", exc)
            raise StrategyError("MACDStrategy computation failed")
