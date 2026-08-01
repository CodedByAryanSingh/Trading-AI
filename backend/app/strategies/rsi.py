"""Relative Strength Index strategy."""
from __future__ import annotations
import pandas as pd
from .base import Signal, Strategy

class RSIStrategy(Strategy):
    def __init__(self, data: pd.DataFrame, window: int = 14, lower: float = 30, upper: float = 70):
        super().__init__(data); self.window = window; self.lower = lower; self.upper = upper
    def generate(self) -> Signal:
        if len(self.data) < self.window + 1:
            return Signal("HOLD", 0.0, {"error": "Insufficient data"})
        delta = self.data["Close"].diff()
        gain  = delta.where(delta > 0, 0).rolling(self.window).mean()
        loss  = (-delta.where(delta < 0, 0)).rolling(self.window).mean()
        rs    = gain / loss
        rsi_s = 100 - (100 / (1 + rs))
        rsi, prev_rsi = float(rsi_s.iloc[-1]), float(rsi_s.iloc[-2])
        if pd.isna(rsi): return Signal("HOLD", 0.0, {"error": "Cannot calculate RSI"})
        if prev_rsi < self.lower and rsi >= self.lower:
            return Signal("BUY",  min(1.0, (self.lower - rsi) / self.lower + 0.5), {"rsi": rsi, "condition": "oversold_bounce"})
        if prev_rsi > self.upper and rsi <= self.upper:
            return Signal("SELL", min(1.0, (rsi - self.upper) / (100 - self.upper) + 0.5), {"rsi": rsi, "condition": "overbought_reversal"})
        if rsi < self.lower: return Signal("BUY",  0.6, {"rsi": rsi, "condition": "oversold"})
        if rsi > self.upper: return Signal("SELL", 0.6, {"rsi": rsi, "condition": "overbought"})
        return Signal("HOLD", 0.2, {"rsi": rsi, "condition": "neutral"})
