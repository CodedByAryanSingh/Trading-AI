"""Breakout strategy based on support/resistance levels."""
from __future__ import annotations

import pandas as pd

from .base import Signal, Strategy


class BreakoutStrategy(Strategy):
    """Breakout strategy using recent highs/lows."""

    def __init__(self, data: pd.DataFrame, lookback: int = 20):
        super().__init__(data)
        self.lookback = lookback

    def generate(self) -> Signal:
        """Generate signal based on breakout from recent range."""
        if len(self.data) < self.lookback + 1:
            return Signal("HOLD", 0.0, {"error": "Insufficient data"})

        recent = self.data["Close"].iloc[-self.lookback:]
        high = recent.max()
        low = recent.min()
        current = self.data["Close"].iloc[-1]
        prev = self.data["Close"].iloc[-2]
        volume = self.data.get("Volume", pd.Series([0] * len(self.data)))
        avg_volume = volume.iloc[-self.lookback:].mean()
        curr_volume = volume.iloc[-1]

        if pd.isna(high) or pd.isna(low):
            return Signal("HOLD", 0.0, {"error": "Cannot calculate levels"})

        range_size = high - low
        if range_size == 0:
            return Signal("HOLD", 0.0, {"error": "Invalid range"})

        # Volume confirmation
        volume_confirmed = curr_volume > avg_volume * 1.2 if avg_volume > 0 else False

        # Breakout above resistance
        if prev <= high and current > high:
            confidence = min(1.0, (current - high) / range_size + (0.2 if volume_confirmed else 0))
            return Signal("BUY", confidence, {
                "resistance": float(high),
                "support": float(low),
                "breakout": "up",
                "volume_confirmed": volume_confirmed,
            })

        # Breakdown below support
        if prev >= low and current < low:
            confidence = min(1.0, (low - current) / range_size + (0.2 if volume_confirmed else 0))
            return Signal("SELL", confidence, {
                "resistance": float(high),
                "support": float(low),
                "breakout": "down",
                "volume_confirmed": volume_confirmed,
            })

        # Near resistance
        if current > high * 0.99:
            return Signal("HOLD", 0.4, {
                "resistance": float(high),
                "support": float(low),
                "proximity": "near_resistance",
            })

        # Near support
        if current < low * 1.01:
            return Signal("HOLD", 0.4, {
                "resistance": float(high),
                "support": float(low),
                "proximity": "near_support",
            })

        return Signal("HOLD", 0.1, {
            "resistance": float(high),
            "support": float(low),
            "position": "mid_range",
        })
