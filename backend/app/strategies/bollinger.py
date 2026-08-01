"""Bollinger Bands strategy."""
from __future__ import annotations
import pandas as pd
from .base import Signal, Strategy

class BollingerStrategy(Strategy):
    def __init__(self, data: pd.DataFrame, window: int = 20, num_std: float = 2.0):
        super().__init__(data); self.window = window; self.num_std = num_std
    def generate(self) -> Signal:
        if len(self.data) < self.window:
            return Signal("HOLD", 0.0, {"error": "Insufficient data"})
        sma   = self.data["Close"].rolling(self.window).mean()
        std   = self.data["Close"].rolling(self.window).std()
        upper = sma + std * self.num_std
        lower = sma - std * self.num_std
        cp, cu, cl, cs, pp = float(self.data["Close"].iloc[-1]), float(upper.iloc[-1]), float(lower.iloc[-1]), float(sma.iloc[-1]), float(self.data["Close"].iloc[-2])
        if pd.isna(cu) or pd.isna(cl): return Signal("HOLD", 0.0, {"error": "Cannot calculate Bollinger Bands"})
        if pp <= cl and cp > cl: return Signal("BUY",  min(1.0, (cs - cp) / (cs - cl) if cs != cl else 0.5), {"price": cp, "upper": cu, "lower": cl, "condition": "lower_bounce"})
        if pp >= cu and cp < cu: return Signal("SELL", min(1.0, (cp - cs) / (cu - cs) if cu != cs else 0.5), {"price": cp, "upper": cu, "lower": cl, "condition": "upper_reversal"})
        if cp < cl: return Signal("BUY",  0.7, {"price": cp, "upper": cu, "lower": cl, "condition": "below_lower"})
        if cp > cu: return Signal("SELL", 0.7, {"price": cp, "upper": cu, "lower": cl, "condition": "above_upper"})
        return Signal("HOLD", 0.2, {"price": cp, "upper": cu, "lower": cl, "condition": "within_bands"})
