"""Trend following strategy using ADX."""
from __future__ import annotations

import pandas as pd

from .base import Signal, Strategy


class TrendStrategy(Strategy):
    """Trend following strategy using price momentum."""

    def __init__(self, data: pd.DataFrame, lookback: int = 20):
        super().__init__(data)
        self.lookback = lookback

    def generate(self) -> Signal:
        """Generate signal based on trend strength."""
        if len(self.data) < self.lookback + 1:
            return Signal("HOLD", 0.0, {"error": "Insufficient data"})

        # Simple trend: compare current price to N-period ago
        current = self.data["Close"].iloc[-1]
        past = self.data["Close"].iloc[-self.lookback - 1]

        # Calculate simple moving average slope
        sma = self.data["Close"].rolling(window=self.lookback).mean()
        curr_sma = sma.iloc[-1]
        prev_sma = sma.iloc[-2] if len(sma) > 1 else curr_sma

        if pd.isna(curr_sma) or pd.isna(prev_sma):
            return Signal("HOLD", 0.0, {"error": "Cannot calculate trend"})

        # Determine trend direction and strength
        price_change = (current - past) / past if past != 0 else 0
        sma_slope = curr_sma - prev_sma

        # Strong uptrend
        if price_change > 0.05 and sma_slope > 0:
            confidence = min(1.0, abs(price_change) * 5 + 0.3)
            return Signal("BUY", confidence, {
                "price_change": float(price_change),
                "sma_slope": float(sma_slope),
                "trend": "strong_up",
            })

        # Strong downtrend
        if price_change < -0.05 and sma_slope < 0:
            confidence = min(1.0, abs(price_change) * 5 + 0.3)
            return Signal("SELL", confidence, {
                "price_change": float(price_change),
                "sma_slope": float(sma_slope),
                "trend": "strong_down",
            })

        # Weak uptrend
        if price_change > 0 and sma_slope > 0:
            return Signal("BUY", 0.3, {
                "price_change": float(price_change),
                "sma_slope": float(sma_slope),
                "trend": "weak_up",
            })

        # Weak downtrend
        if price_change < 0 and sma_slope < 0:
            return Signal("SELL", 0.3, {
                "price_change": float(price_change),
                "sma_slope": float(sma_slope),
                "trend": "weak_down",
            })

        return Signal("HOLD", 0.2, {
            "price_change": float(price_change),
            "sma_slope": float(sma_slope),
            "trend": "neutral",
        })
