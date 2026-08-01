"""Simple Moving Average crossover strategy."""
from __future__ import annotations
import pandas as pd
from .base import Signal, Strategy

class SMAStrategy(Strategy):
    def __init__(self, data: pd.DataFrame, short_window: int = 50, long_window: int = 200):
        super().__init__(data); self.short_window = short_window; self.long_window = long_window
    def generate(self) -> Signal:
        if len(self.data) < self.long_window:
            return Signal("HOLD", 0.0, {"error": "Insufficient data"})
        short_sma = self.data["Close"].rolling(self.short_window).mean()
        long_sma  = self.data["Close"].rolling(self.long_window).mean()
        s, l, ps, pl = float(short_sma.iloc[-1]), float(long_sma.iloc[-1]), float(short_sma.iloc[-2]), float(long_sma.iloc[-2])
        if ps <= pl and s > l:
            return Signal("BUY",  min(1.0, abs(s-l)/l*100), {"short_sma": s, "long_sma": l, "cross": "golden"})
        if ps >= pl and s < l:
            return Signal("SELL", min(1.0, abs(s-l)/l*100), {"short_sma": s, "long_sma": l, "cross": "death"})
        sig = "BUY" if s > l else "SELL"
        return Signal(sig, 0.3 + min(0.4, abs(s-l)/l*50), {"short_sma": s, "long_sma": l, "trend": "up" if s > l else "down"})
