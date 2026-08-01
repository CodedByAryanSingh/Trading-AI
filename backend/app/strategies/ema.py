"""Exponential Moving Average crossover strategy."""
from __future__ import annotations
import pandas as pd
from .base import Signal, Strategy

class EMAStrategy(Strategy):
    def __init__(self, data: pd.DataFrame, short_span: int = 12, long_span: int = 26):
        super().__init__(data); self.short_span = short_span; self.long_span = long_span
    def generate(self) -> Signal:
        if len(self.data) < self.long_span:
            return Signal("HOLD", 0.0, {"error": "Insufficient data"})
        se = self.data["Close"].ewm(span=self.short_span, adjust=False).mean()
        le = self.data["Close"].ewm(span=self.long_span,  adjust=False).mean()
        s, l, ps, pl = float(se.iloc[-1]), float(le.iloc[-1]), float(se.iloc[-2]), float(le.iloc[-2])
        if ps <= pl and s > l: return Signal("BUY",  min(1.0, abs(s-l)/l*100), {"short_ema": s, "long_ema": l, "cross": "bullish"})
        if ps >= pl and s < l: return Signal("SELL", min(1.0, abs(s-l)/l*100), {"short_ema": s, "long_ema": l, "cross": "bearish"})
        return Signal("BUY" if s > l else "SELL", 0.4, {"short_ema": s, "long_ema": l, "trend": "up" if s > l else "down"})
