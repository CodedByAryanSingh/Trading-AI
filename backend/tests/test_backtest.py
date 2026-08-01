"""Backtest engine tests."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from app.backtest.engine import BacktestEngine
from app.backtest.metrics import calculate_metrics
from app.backtest.report import generate_report


def create_backtest_data(n: int = 200) -> pd.DataFrame:
    """Generate sample data with signals for backtesting."""
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", periods=n, freq="D")
    price = 100 + np.cumsum(np.random.randn(n) * 0.5)

    df = pd.DataFrame({
        "Open": price + np.random.randn(n) * 0.2,
        "High": price + abs(np.random.randn(n)) * 0.5,
        "Low": price - abs(np.random.randn(n)) * 0.5,
        "Close": price,
        "Volume": np.random.randint(1000000, 10000000, n),
    }, index=dates)

    # Simple SMA crossover signals
    df["sma_short"] = df["Close"].rolling(10).mean()
    df["sma_long"] = df["Close"].rolling(30).mean()
    df["signal"] = 0
    df.loc[df["sma_short"] > df["sma_long"], "signal"] = 1
    df.loc[df["sma_short"] < df["sma_long"], "signal"] = -1

    return df.dropna()


class TestBacktestEngine:
    def test_run_backtest(self):
        data = create_backtest_data()
        engine = BacktestEngine(initial_cash=100000.0)
        engine.run(data, signal_column="signal")

        assert len(engine.equity_curve) == len(data)
        summary = engine.summary()

        assert "total_return" in summary
        assert "sharpe_ratio" in summary
        assert "max_drawdown" in summary

    def test_no_data_error(self):
        engine = BacktestEngine()
        with pytest.raises(ValueError):
            engine.run(pd.DataFrame(), signal_column="signal")


class TestMetrics:
    def test_calculate_metrics(self):
        data = create_backtest_data()
        engine = BacktestEngine(initial_cash=100000.0)
        engine.run(data, signal_column="signal")

        metrics = calculate_metrics(engine.trades, engine.equity_dataframe())

        assert "total_return_pct" in metrics
        assert "sharpe_ratio" in metrics
        assert "max_drawdown_pct" in metrics


class TestReport:
    def test_generate_report(self):
        data = create_backtest_data()
        engine = BacktestEngine(initial_cash=100000.0)
        engine.run(data, signal_column="signal")

        report = generate_report(engine.trades, engine.equity_dataframe())

        assert "summary" in report
        assert "trades" in report
        assert "equity" in report
