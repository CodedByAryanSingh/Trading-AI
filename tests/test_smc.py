"""
Unit tests for Smart Money Concepts detector (SMCDetector).

These tests use synthetic price series crafted to produce deterministic
BOS (Break of Structure), FVG (Fair Value Gap), and order block
candidates to validate the heuristics in indicators/smc.py.
"""
from __future__ import annotations

import pandas as pd

from indicators.smc import SMCDetector


def make_simple_bos_series():
    # Create a slow uptrend and then a breakout
    closes = [100, 101, 100.5, 101.5, 102, 101.8, 103, 104, 110]
    highs = [c + 0.5 for c in closes]
    lows = [c - 0.5 for c in closes]
    df = pd.DataFrame({"High": highs, "Low": lows, "Close": closes})
    return df


def test_bos_detected():
    df = make_simple_bos_series()
    det = SMCDetector(df)
    pivots = det.find_pivots(left=1, right=1)
    bos = det.detect_bos(pivots)
    # Expect at least one bullish BOS from the final large close
    assert any(e["side"] == "bull" for e in bos), f"No bullish BOS found: {bos}"


def make_fvg_series():
    # Create a small gap between candle 2 and 3 to simulate FVG
    closes = [100, 101, 103, 106]
    highs = [c + 0.5 for c in closes]
    lows = [c - 0.5 for c in closes]
    # Insert an up gap artificially: make lows[3] > highs[2]
    lows[3] = highs[2] + 0.2
    df = pd.DataFrame({"High": highs, "Low": lows, "Close": closes})
    return df


def test_fvg_detected():
    df = make_fvg_series()
    det = SMCDetector(df)
    fvg = det.detect_fvg()
    assert len(fvg) >= 1
    assert any(z.side == "bull" for z in fvg)


def make_order_block_series():
    # prior bearish candle followed by strong bullish move
    opens = [110, 109, 108, 108.5]
    closes = [109, 108, 107, 112]
    highs = [max(o, c) + 0.5 for o, c in zip(opens, closes)]
    lows = [min(o, c) - 0.5 for o, c in zip(opens, closes)]
    df = pd.DataFrame({"Open": opens, "High": highs, "Low": lows, "Close": closes})
    return df


def test_order_block_detected():
    df = make_order_block_series()
    det = SMCDetector(df)
    obs = det.detect_order_blocks()
    assert len(obs) >= 1
    assert any(z.side == "bull" or z.side == "bear" for z in obs)
