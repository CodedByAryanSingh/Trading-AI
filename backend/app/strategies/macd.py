"""MACD strategy."""
from __future__ import annotations
import pandas as pd
from .base import Signal, Strategy

class MACDStrategy(Strategy):
    def __init__(self, data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9):
        super().__init__(data); self.fast = fast; self.slow = slow; self.signal = signal
    def generate(self) -> Signal:
        if len(self.data) < self.slow + self.signal:
            return Signal("HOLD", 0.0, {"error": "Insufficient data"})
        e1  = self.data["Close"].ewm(span=self.fast,   adjust=False).mean()
        e2  = self.data["Close"].ewm(span=self.slow,   adjust=False).mean()
        mac = e1 - e2
        sig = mac.ewm(span=self.signal, adjust=False).mean()
        hst = mac - sig
        cm, cs, pm, ps = float(mac.iloc[-1]), float(sig.iloc[-1]), float(mac.iloc[-2]), float(sig.iloc[-2])
        if pd.isna(cm) or pd.isna(cs): return Signal("HOLD", 0.0, {"error": "Cannot calculate MACD"})
        conf = min(1.0, abs(cm-cs)/abs(cs) if cs != 0 else 0.5)
        if pm <= ps and cm > cs: return Signal("BUY",  conf, {"macd": cm, "signal": cs, "histogram": float(hst.iloc[-1]), "cross": "bullish"})
        if pm >= ps and cm < cs: return Signal("SELL", conf, {"macd": cm, "signal": cs, "histogram": float(hst.iloc[-1]), "cross": "bearish"})
        return Signal("BUY" if cm > cs else "SELL", 0.35, {"macd": cm, "signal": cs, "trend": "bullish" if cm > cs else "bearish"})
