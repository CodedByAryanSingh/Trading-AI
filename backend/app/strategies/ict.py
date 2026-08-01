"""Inner Circle Trader (ICT) strategy."""
from __future__ import annotations

import pandas as pd

from .base import Signal, Strategy


class ICTStrategy(Strategy):
    """ICT strategy focusing on market structure and killzones."""

    def __init__(self, data: pd.DataFrame, lookback: int = 10):
        super().__init__(data)
        self.lookback = lookback

    def _detect_structure(self):
        """Detect bullish/bearish market structure."""
        highs = self.data["High"].iloc[-self.lookback:]
        lows = self.data["Low"].iloc[-self.lookback:]

        # Higher highs and higher lows = bullish
        hh = highs.iloc[-1] > highs.max() * 0.99
        hl = lows.iloc[-1] > lows.mean()

        # Lower highs and lower lows = bearish
        lh = highs.iloc[-1] < highs.mean()
        ll = lows.iloc[-1] < lows.min() * 1.01

        return hh, hl, lh, ll

    def _liquidity_sweep(self):
        """Detect liquidity sweeps beyond recent highs/lows."""
        if len(self.data) < self.lookback + 2:
            return False, False

        prev_high = self.data["High"].iloc[-self.lookback-1:-1].max()
        prev_low = self.data["Low"].iloc[-self.lookback-1:-1].min()

        curr_high = self.data["High"].iloc[-1]
        curr_low = self.data["Low"].iloc[-1]
        curr_close = self.data["Close"].iloc[-1]

        # Buy-side liquidity sweep: wick above previous high, close below
        buy_sweep = curr_high > prev_high and curr_close < prev_high

        # Sell-side liquidity sweep: wick below previous low, close above
        sell_sweep = curr_low < prev_low and curr_close > prev_low

        return buy_sweep, sell_sweep

    def generate(self) -> Signal:
        """Generate signal based on ICT concepts."""
        if len(self.data) < self.lookback + 2:
            return Signal("HOLD", 0.0, {"error": "Insufficient data"})

        hh, hl, lh, ll = self._detect_structure()
        buy_sweep, sell_sweep = self._liquidity_sweep()
        current = self.data["Close"].iloc[-1]

        # Bullish scenario: liquidity sweep + bullish structure
        if sell_sweep and (hh or hl):
            return Signal("BUY", 0.75, {
                "sell_sweep": sell_sweep,
                "higher_high": hh,
                "higher_low": hl,
                "concept": "liquidity_sweep_bullish",
            })

        # Bearish scenario: liquidity sweep + bearish structure
        if buy_sweep and (lh or ll):
            return Signal("SELL", 0.75, {
                "buy_sweep": buy_sweep,
                "lower_high": lh,
                "lower_low": ll,
                "concept": "liquidity_sweep_bearish",
            })

        # Bias only from structure
        if hh and hl:
            return Signal("BUY", 0.4, {
                "structure": "bullish",
                "higher_high": hh,
                "higher_low": hl,
            })

        if lh and ll:
            return Signal("SELL", 0.4, {
                "structure": "bearish",
                "lower_high": lh,
                "lower_low": ll,
            })

        return Signal("HOLD", 0.15, {
            "structure": "neutral",
            "higher_high": hh,
            "lower_low": ll,
        })
