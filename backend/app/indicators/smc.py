"""Smart Money Concepts indicator helpers."""
from __future__ import annotations

from typing import List

import pandas as pd


def detect_order_blocks(data: pd.DataFrame, lookback: int = 5) -> List[dict]:
    """Detect bullish and bearish order blocks."""
    obs = []

    for i in range(1, len(data) - 1):
        prev = data.iloc[i - 1]
        curr = data.iloc[i]
        next_c = data.iloc[i + 1]

        # Bullish OB: bearish candle before strong bullish move
        if prev["Close"] < prev["Open"] and next_c["Close"] > next_c["Open"] and next_c["Close"] > prev["High"]:
            obs.append({
                "type": "bullish",
                "index": i,
                "high": float(prev["High"]),
                "low": float(prev["Low"]),
                "open": float(prev["Open"]),
                "close": float(prev["Close"]),
            })

        # Bearish OB: bullish candle followed by strong bearish move
        if prev["Close"] > prev["Open"] and next_c["Close"] < next_c["Open"] and next_c["Close"] < prev["Low"]:
            obs.append({
                "type": "bearish",
                "index": i,
                "high": float(prev["High"]),
                "low": float(prev["Low"]),
                "open": float(prev["Open"]),
                "close": float(prev["Close"]),
            })

    return obs


def detect_fvg(data: pd.DataFrame) -> List[dict]:
    """Detect Fair Value Gaps."""
    fvgs = []

    for i in range(2, len(data)):
        c1 = data.iloc[i - 2]
        c2 = data.iloc[i - 1]
        c3 = data.iloc[i]

        # Bullish FVG: c1 high < c3 low
        if c1["High"] < c3["Low"]:
            fvgs.append({
                "type": "bullish",
                "index": i,
                "top": float(c3["Low"]),
                "bottom": float(c1["High"]),
            })

        # Bearish FVG: c1 low > c3 high
        if c1["Low"] > c3["High"]:
            fvgs.append({
                "type": "bearish",
                "index": i,
                "top": float(c1["Low"]),
                "bottom": float(c3["High"]),
            })

    return fvgs
