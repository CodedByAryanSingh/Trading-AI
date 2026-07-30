"""
Unit tests for StrategyEngine core methods.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.strategy import StrategyEngine


def make_trending_df(periods: int = 100):
    idx = pd.date_range(end=pd.Timestamp.now(), periods=periods, freq="D")
    prices = pd.Series(np.linspace(100, 200, periods), index=idx)
    return pd.DataFrame({"Close": prices})


def test_sma_signal_basic():
    df = make_trending_df(100)
    engine = StrategyEngine(df)
    out = engine.sma_signal(short=5, long=20)
    assert out["signal"] in {"BUY", "SELL", "HOLD"}
    assert 0.0 <= out["confidence"] <= 1.0


def test_multi_confirmation_runs():
    df = make_trending_df(200)
    engine = StrategyEngine(df)
    out = engine.multi_indicator_confirmation()
    assert "signal" in out
    assert "confidence" in out
