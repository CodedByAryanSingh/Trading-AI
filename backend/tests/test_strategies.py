"""Strategy logic tests."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from app.strategies.base import Signal, Strategy, StrategyError
from app.strategies.sma import SMAStrategy
from app.strategies.ema import EMAStrategy
from app.strategies.rsi import RSIStrategy
from app.strategies.macd import MACDStrategy
from app.strategies.bollinger import BollingerStrategy
from app.strategies.trend import TrendStrategy
from app.strategies.breakout import BreakoutStrategy
from app.strategies.smc import SMCStrategy
from app.strategies.ict import ICTStrategy
from app.strategies.manager import StrategyManager


def create_sample_data(n: int = 300) -> pd.DataFrame:
    """Generate sample OHLCV data."""
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", periods=n, freq="D")
    price = 100 + np.cumsum(np.random.randn(n) * 0.5)

    return pd.DataFrame({
        "Open": price + np.random.randn(n) * 0.2,
        "High": price + abs(np.random.randn(n)) * 0.5,
        "Low": price - abs(np.random.randn(n)) * 0.5,
        "Close": price,
        "Volume": np.random.randint(1000000, 10000000, n),
    }, index=dates)


class TestBaseStrategy:
    def test_strategy_error(self):
        with pytest.raises(StrategyError):
            Strategy(data="not a dataframe")

    def test_signal_dataclass(self):
        sig = Signal("BUY", 0.8, {"key": "value"})
        assert sig.signal == "BUY"
        assert sig.confidence == 0.8


class TestSMAStrategy:
    def test_generate(self):
        data = create_sample_data()
        strat = SMAStrategy(data, short_window=10, long_window=50)
        sig = strat.generate()
        assert sig.signal in ["BUY", "SELL", "HOLD"]
        assert 0 <= sig.confidence <= 1


class TestEMAStrategy:
    def test_generate(self):
        data = create_sample_data()
        strat = EMAStrategy(data, short_span=12, long_span=26)
        sig = strat.generate()
        assert sig.signal in ["BUY", "SELL", "HOLD"]


class TestRSIStrategy:
    def test_generate(self):
        data = create_sample_data()
        strat = RSIStrategy(data, window=14)
        sig = strat.generate()
        assert sig.signal in ["BUY", "SELL", "HOLD"]


class TestMACDStrategy:
    def test_generate(self):
        data = create_sample_data()
        strat = MACDStrategy(data)
        sig = strat.generate()
        assert sig.signal in ["BUY", "SELL", "HOLD"]


class TestBollingerStrategy:
    def test_generate(self):
        data = create_sample_data()
        strat = BollingerStrategy(data, window=20, num_std=2.0)
        sig = strat.generate()
        assert sig.signal in ["BUY", "SELL", "HOLD"]


class TestTrendStrategy:
    def test_generate(self):
        data = create_sample_data()
        strat = TrendStrategy(data, lookback=20)
        sig = strat.generate()
        assert sig.signal in ["BUY", "SELL", "HOLD"]


class TestBreakoutStrategy:
    def test_generate(self):
        data = create_sample_data()
        strat = BreakoutStrategy(data, lookback=20)
        sig = strat.generate()
        assert sig.signal in ["BUY", "SELL", "HOLD"]


class TestSMCStrategy:
    def test_generate(self):
        data = create_sample_data()
        strat = SMCStrategy(data, swing_lookback=5)
        sig = strat.generate()
        assert sig.signal in ["BUY", "SELL", "HOLD"]


class TestICTStrategy:
    def test_generate(self):
        data = create_sample_data()
        strat = ICTStrategy(data, lookback=10)
        sig = strat.generate()
        assert sig.signal in ["BUY", "SELL", "HOLD"]


class TestStrategyManager:
    def test_aggregate(self):
        data = create_sample_data()
        manager = StrategyManager(data)
        manager.auto_register_defaults()
        result = manager.aggregate()

        assert "signal" in result
        assert "confidence" in result
        assert "score" in result
        assert "breakdown" in result
        assert len(result["breakdown"]) > 0
