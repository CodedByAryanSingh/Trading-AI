"""Reporting helpers for backtest results.

Provides functions to build a summary report and DataFrame outputs from a
BacktestEngine run. These are kept separate from the engine to make unit
testing and extension straightforward.
"""
from __future__ import annotations

from typing import Dict, List

import pandas as pd

from .metrics import cagr, max_drawdown, sharpe_ratio, sortino_ratio, trade_statistics


def build_summary(equity_curve: pd.Series, trades: List[dict]) -> Dict[str, object]:
    """Build a compact summary dictionary from equity and trades.

    Args:
        equity_curve: pd.Series of equity values indexed by datetime
        trades: list of trade dicts produced by BacktestEngine

    Returns:
        Dictionary with key performance indicators
    """
    stats = trade_statistics(trades)
    summary = {
        "start_date": None if equity_curve.empty else str(equity_curve.index[0]),
        "end_date": None if equity_curve.empty else str(equity_curve.index[-1]),
        "start_equity": float(equity_curve.iloc[0]) if not equity_curve.empty else 0.0,
        "end_equity": float(equity_curve.iloc[-1]) if not equity_curve.empty else 0.0,
        "cagr": cagr(equity_curve),
        "max_drawdown": max_drawdown(equity_curve),
        "sharpe": sharpe_ratio(equity_curve),
        "sortino": sortino_ratio(equity_curve),
    }
    summary.update(stats)
    return summary


def trades_to_df(trades: List[dict]) -> pd.DataFrame:
    """Convert trade list into a pandas DataFrame for easy inspection.

    The DataFrame will contain columns such as entry_time, exit_time, entry_price,
    exit_price, size, pnl, return_pct, fees.
    """
    if not trades:
        return pd.DataFrame()
    return pd.DataFrame(trades)
