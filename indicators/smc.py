"""
Smart Money Concepts (SMC) detection utilities.

This module implements a best-effort, unit-testable SMCDetector that
identifies structural features useful for SMC-based strategies:
- Pivot highs/lows
- Break of Structure (BOS)
- Change of Character (CHoCH)
- Fair Value Gaps (FVG)
- Simple Order Block detection (heuristic)
- Liquidity sweeps and equal highs/lows

The implementations are intentionally conservative and deterministic so
unit tests can validate behavior on synthetic series. In production,
these rules should be tuned and augmented with volume/session context.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pandas as pd
import numpy as np

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Zone:
    """Represents a detected price zone such as an order block or FVG.

    Attributes:
        start_idx: integer index of zone start (position in DataFrame)
        end_idx: integer index of zone end (position in DataFrame)
        top: price (upper bound)
        bottom: price (lower bound)
        side: 'bull'|'bear'|'neutral'
        strength: float heuristic 0..1 (higher => stronger)
    """

    start_idx: int
    end_idx: int
    top: float
    bottom: float
    side: str
    strength: float = 0.0


class SMCDetector:
    """Detector for Smart Money Concepts on OHLCV data.

    The detector focuses on price structure computations using High/Low/
    Close columns. It avoids using volume-dependent rules for determinism
    in unit tests, but can incorporate volume if provided in the DataFrame.
    """

    def __init__(self, df: pd.DataFrame) -> None:
        """Initialize the detector.

        Args:
            df: DataFrame indexed by time with columns: 'High','Low','Close'
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")
        required = {"High", "Low", "Close"}
        if not required.issubset(set(df.columns)):
            raise ValueError(f"DataFrame must contain columns: {required}")
        self.df = df.copy().reset_index(drop=True)

    def find_pivots(self, left: int = 3, right: int = 3) -> List[Dict[str, int]]:
        """Find pivot highs and lows.

        A pivot high at index i is defined as High[i] being the maximum in
        the window [i-left, i+right]. Pivot low analogously with minimum.

        Args:
            left: bars to the left to consider
            right: bars to the right to consider

        Returns:
            List of dicts: { 'type': 'high'|'low', 'index': i }
        """
        highs = self.df["High"].values
        lows = self.df["Low"].values
        n = len(self.df)
        pivots: List[Dict[str, int]] = []
        for i in range(left, n - right):
            win_h = highs[i - left : i + right + 1]
            win_l = lows[i - left : i + right + 1]
            if highs[i] == np.max(win_h) and list(win_h).count(highs[i]) == 1:
                pivots.append({"type": "high", "index": int(i)})
            if lows[i] == np.min(win_l) and list(win_l).count(lows[i]) == 1:
                pivots.append({"type": "low", "index": int(i)})
        logger.debug("Found %d pivots", len(pivots))
        return pivots

    def detect_bos(self, pivots: Optional[List[Dict[str, int]]] = None) -> List[Dict[str, object]]:
        """Detect Break of Structure (BOS) events.

        A bullish BOS occurs when price closes above the most recent pivot
        high (structure high). A bearish BOS occurs when price closes below
        the most recent pivot low.

        Returns:
            List of BOS events: { 'side': 'bull'|'bear', 'index': i, 'price': float, 'pivot_index': int }
        """
        pivots = pivots or self.find_pivots()
        events: List[Dict[str, object]] = []
        # collect pivot highs and lows separately
        pivot_highs = [p["index"] for p in pivots if p["type"] == "high"]
        pivot_lows = [p["index"] for p in pivots if p["type"] == "low"]

        # iterate candles after the earliest pivot to find closes breaking pivots
        for i in range(len(self.df)):
            close = float(self.df.at[i, "Close"])  # type: ignore[index]
            # bullish BOS: close > last pivot high
            last_high = max([idx for idx in pivot_highs if idx < i], default=None)
            if last_high is not None:
                high_val = float(self.df.at[last_high, "High"])  # type: ignore[index]
                if close > high_val:
                    events.append({"side": "bull", "index": int(i), "price": close, "pivot_index": int(last_high)})
            # bearish BOS: close < last pivot low
            last_low = max([idx for idx in pivot_lows if idx < i], default=None)
            if last_low is not None:
                low_val = float(self.df.at[last_low, "Low"])  # type: ignore[index]
                if close < low_val:
                    events.append({"side": "bear", "index": int(i), "price": close, "pivot_index": int(last_low)})
        logger.debug("Detected %d BOS events", len(events))
        return events

    def detect_choch(self, bos_events: Optional[List[Dict[str, object]]] = None) -> List[Dict[str, object]]:
        """Detect Change of Character (CHoCH) events.

        A CHoCH is observed when the side of BOS changes (e.g., bull -> bear)
        indicating a potential market structure shift.
        """
        bos_events = bos_events or self.detect_bos()
        choch: List[Dict[str, object]] = []
        for a, b in zip(bos_events, bos_events[1:]):
            if a["side"] != b["side"]:
                choch.append({"from": a, "to": b, "index": b["index"]})
        logger.debug("Detected %d CHoCH events", len(choch))
        return choch

    def detect_fvg(self) -> List[Zone]:
        """Detect Fair Value Gaps (FVG).

        Heuristic: a bullish FVG exists when a candle's Low is greater than
        the previous candle's High (up gap). A bearish FVG when a candle's
        High is less than the previous candle's Low (down gap).

        Returns:
            List of Zone objects with top/bottom prices and indices.
        """
        zones: List[Zone] = []
        highs = self.df["High"].values
        lows = self.df["Low"].values
        n = len(self.df)
        for i in range(1, n):
            # bullish gap
            if float(lows[i]) > float(highs[i - 1]):
                top = float(lows[i])
                bottom = float(highs[i - 1])
                zones.append(Zone(start_idx=i - 1, end_idx=i, top=top, bottom=bottom, side="bull", strength=float(top - bottom)))
            # bearish gap
            if float(highs[i]) < float(lows[i - 1]):
                top = float(lows[i - 1])
                bottom = float(highs[i])
                zones.append(Zone(start_idx=i - 1, end_idx=i, top=top, bottom=bottom, side="bear", strength=float(top - bottom)))
        logger.debug("Detected %d FVG zones", len(zones))
        return zones

    def detect_order_blocks(self, lookback: int = 3) -> List[Zone]:
        """Simple heuristic for detecting order blocks.

        Heuristic:
        - Bullish order block: a bearish candle (close < open) followed by
          a strong bullish move that breaks structure (BOS). The order block
          zone is the high/low of the bearish candle.
        - Bearish order block: analogous reversed.

        Args:
            lookback: number of candles to consider for contiguous candles

        Returns:
            List of Zone objects representing order blocks.
        """
        zones: List[Zone] = []
        o = self.df.get("Open")
        c = self.df.get("Close")
        h = self.df.get("High")
        l = self.df.get("Low")

        if o is None or c is None:
            return zones

        n = len(self.df)
        for i in range(1, n - 1):
            # check for bearish order block candidate: prior candle bearish
            if float(c.iat[i - 1]) < float(o.iat[i - 1]) and float(c.iat[i]) > float(o.iat[i]):
                # bullish response candle exists; define zone as prior candle range
                top = float(h.iat[i - 1])
                bottom = float(l.iat[i - 1])
                strength = abs(float(c.iat[i]) - float(c.iat[i - 1]))
                zones.append(Zone(start_idx=i - 1, end_idx=i - 1, top=top, bottom=bottom, side="bull", strength=float(strength)))
            # check for bullish order block candidate: prior candle bullish then bearish response
            if float(c.iat[i - 1]) > float(o.iat[i - 1]) and float(c.iat[i]) < float(o.iat[i]):
                top = float(h.iat[i - 1])
                bottom = float(l.iat[i - 1])
                strength = abs(float(c.iat[i]) - float(c.iat[i - 1]))
                zones.append(Zone(start_idx=i - 1, end_idx=i - 1, top=top, bottom=bottom, side="bear", strength=float(strength)))
        logger.debug("Detected %d order block zones", len(zones))
        return zones

    def detect_equal_highs_lows(self, tolerance: float = 1e-6) -> Dict[str, List[int]]:
        """Detect approximately equal highs and lows.

        Args:
            tolerance: price tolerance for equality.

        Returns:
            Dict with keys 'equal_highs' and 'equal_lows' listing indices.
        """
        highs = self.df["High"].values
        lows = self.df["Low"].values
        equal_highs: List[int] = []
        equal_lows: List[int] = []
        n = len(self.df)
        for i in range(1, n):
            if abs(highs[i] - highs[i - 1]) <= tolerance:
                equal_highs.append(i)
            if abs(lows[i] - lows[i - 1]) <= tolerance:
                equal_lows.append(i)
        logger.debug("Found %d equal highs and %d equal lows", len(equal_highs), len(equal_lows))
        return {"equal_highs": equal_highs, "equal_lows": equal_lows}

    def detect_liquidity_sweeps(self, wick_threshold: float = 0.002) -> List[Dict[str, object]]:
        """Detect simple liquidity sweeps using long wicks beyond recent range.

        Heuristic: a wick (upper or lower) that exceeds the recent n-bar range
        by wick_threshold fraction of price may indicate a liquidity sweep.
        """
        res: List[Dict[str, object]] = []
        highs = self.df["High"].values
        lows = self.df["Low"].values
        closes = self.df["Close"].values
        n = len(self.df)
        lookback = 20
        for i in range(lookback, n):
            recent_hi = max(highs[i - lookback : i])
            recent_lo = min(lows[i - lookback : i])
            upper_wick = float(highs[i]) - float(max(closes[i], self.df.at[i, "Open"])) if "Open" in self.df.columns else float(highs[i]) - float(closes[i])
            lower_wick = float(min(closes[i], self.df.at[i, "Open"]) ) - float(lows[i]) if "Open" in self.df.columns else float(closes[i]) - float(lows[i])
            price = float(closes[i])
            # upper sweep
            if float(highs[i]) > recent_hi and (upper_wick / price) > wick_threshold:
                res.append({"type": "upper", "index": int(i), "price": float(highs[i])})
            # lower sweep
            if float(lows[i]) < recent_lo and (lower_wick / price) > wick_threshold:
                res.append({"type": "lower", "index": int(i), "price": float(lows[i])})
        logger.debug("Detected %d liquidity sweeps", len(res))
        return res


__all__ = ["SMCDetector", "Zone"]
