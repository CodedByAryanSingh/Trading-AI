"""
Unit tests for MarketData.

These tests are small and verify that the MarketData methods are
callable and behave correctly when given synthetic data or invalid
input. External network calls are avoided where practical.
"""
from __future__ import annotations

import pandas as pd
import pytest

from data.market_data import MarketData, MarketDataConfig


def test_clean_missing():
    md = MarketData(MarketDataConfig())
    df = pd.DataFrame({"Close": [1.0, None, 2.0], "Open": [1.0, None, 2.0]})
    out = md.clean_missing(df)
    assert out.isna().sum().sum() == 0
    assert len(out) == 3


def test_cache_path_and_export(tmp_path):
    cfg = MarketDataConfig()
    cfg.cache_dir = tmp_path
    md = MarketData(cfg)
    df = pd.DataFrame({"Close": [1.0, 2.0, 3.0]})
    p = tmp_path / "test.parquet"
    md.export_parquet(df, str(p))
    assert p.exists()
