"""Smart Money Concepts (SMC) strategy."""
from __future__ import annotations

import pandas as pd

from .base import Signal, Strategy


class SMCStrategy(Strategy):
    """Smart Money Concepts strategy detecting order blocks and liquidity."""

    def __init__(self, data: pd.DataFrame, swing_lookback: int = 5):
        super().__init__(data)
        self.swing_lookback = swing_lookback

    def _find_swing_highs_lows(self):
        """Identify swing highs and lows."""
        highs = self.data["High"]
        lows = self.data["Low"]

        swing_highs = []
        swing_lows = []

        for i in range(self.swing_lookback, len(highs) - self.swing_lookback):
            if highs.iloc[i] == highs.iloc[i-self.swing_lookback:i+self.swing_lookback+1].max():
                swing_highs.append((i, highs.iloc[i]))
            if lows.iloc[i] == lows.iloc[i-self.swing_lookback:i+self.swing_lookback+1].min():
                swing_lows.append((i, lows.iloc[i]))

        return swing_highs, swing_lows

    def generate(self) -> Signal:
        """Generate signal based on SMC concepts."""
        if len(self.data) < self.swing_lookback * 3:
            return Signal("HOLD", 0.0, {"error": "Insufficient data"})

        swing_highs, swing_lows = self._find_swing_highs_lows()
        current = self.data["Close"].iloc[-1]

        if not swing_highs or not swing_lows:
            return Signal("HOLD", 0.0, {"error": "No swings found"})

        # Use recent swing levels as liquidity points
        recent_high = swing_highs[-1][1] if swing_highs else current
        recent_low = swing_lows[-1][1] if swing_lows else current

        # Order block detection: strong bullish/bearish candle before move
        recent_candles = self.data.iloc[-5:]
        bullish_ob = False
        bearish_ob = False

        for i in range(1, len(recent_candles)):
            prev = recent_candles.iloc[i-1]
            curr = recent_candles.iloc[i]

            # Bullish order block: bearish candle followed by strong bullish move
            if prev["Close"] < prev["Open"] and curr["Close"] > curr["Open"] and curr["Close"] > prev["High"]:
                bullish_ob = True
                ob_price = prev["Close"]

            # Bearish order block: bullish candle followed by strong bearish move
            if prev["Close"] > prev["Open"] and curr["Close"] < curr["Open"] and curr["Close"] < prev["Low"]:
                bearish_ob = True
                ob_price = prev["Close"]

        # Fair Value Gap detection
        fvg_bullish = False
        fvg_bearish = False

        for i in range(2, len(self.data)):
            c1 = self.data.iloc[i-2]
            c2 = self.data.iloc[i-1]
            c3 = self.data.iloc[i]

            if c1["High"] < c3["Low"]:
                fvg_bullish = True
            if c1["Low"] > c3["High"]:
                fvg_bearish = True

        # Signal generation
        if bullish_ob and current < recent_high * 0.98:
            confidence = 0.6 + (0.1 if fvg_bullish else 0)
            return Signal("BUY", min(1.0, confidence), {
                "recent_high": float(recent_high),
                "recent_low": float(recent_low),
                "bullish_ob": bullish_ob,
                "fvg_bullish": fvg_bullish,
                "concept": "order_block",
            })

        if bearish_ob and current > recent_low * 1.02:
            confidence = 0.6 + (0.1 if fvg_bearish else 0)
            return Signal("SELL", min(1.0, confidence), {
                "recent_high": float(recent_high),
                "recent_low": float(recent_low),
                "bearish_ob": bearish_ob,
                "fvg_bearish": fvg_bearish,
                "concept": "order_block",
            })

        return Signal("HOLD", 0.2, {
            "recent_high": float(recent_high),
            "recent_low": float(recent_low),
            "bullish_ob": bullish_ob,
            "bearish_ob": bearish_ob,
        })
