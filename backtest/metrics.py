"""Performance metrics for backtest results.

Provides functions to compute Sharpe, Sortino, maximum drawdown, win rate,
profit factor, and other common metrics from an equity curve or trade list.

All functions are pure and unit-testable.
"""
from __future__ import annotations

from typing import Iterable, Optional

import numpy as np
import pandas as pd


def _daily_returns_from_equity(equity: pd.Series) -> pd.Series:
    """Compute simple returns from an equity series indexed by time.

    Args:
        equity: pd.Series of equity values indexed by datetime.
    Returns:
        pd.Series of simple returns (pct change)
    """
    return equity.pct_change().fillna(0.0)


def sharpe_ratio(equity: pd.Series, risk_free_rate: float = 0.0, trading_days: int = 252) -> float:
    """Compute annualized Sharpe ratio for an equity curve.

    Uses simple returns (not log returns). If the series is constant returns 0.

    Args:
        equity: pd.Series of equity values indexed by datetime
        risk_free_rate: annualized risk free rate (decimal)
        trading_days: number of trading days per year
    Returns:
        Annualized Sharpe ratio (float)
    """
    if equity.empty:
        return 0.0
    rets = _daily_returns_from_equity(equity)
    mean_ret = rets.mean() * trading_days
    std_ret = rets.std() * (trading_days ** 0.5)
    if std_ret == 0:
        return 0.0
    # Adjust mean_ret by risk-free rate (annualized)
    excess = mean_ret - risk_free_rate
    return float(excess / std_ret)


def sortino_ratio(equity: pd.Series, risk_free_rate: float = 0.0, trading_days: int = 252) -> float:
    """Compute annualized Sortino ratio for an equity curve.

    Only considers downside deviation.
    """
    if equity.empty:
        return 0.0
    rets = _daily_returns_from_equity(equity)
    # downside deviation
    negative_rets = rets[rets < 0]
    if negative_rets.empty:
        return float((rets.mean() * trading_days - risk_free_rate) / 1e-9)
    downside_std = negative_rets.std() * (trading_days ** 0.5)
    if downside_std == 0:
        return 0.0
    excess = rets.mean() * trading_days - risk_free_rate
    return float(excess / downside_std)


def max_drawdown(equity: pd.Series) -> float:
    """Compute maximum drawdown (as a positive decimal) from equity series.

    Returns:
        max drawdown (e.g., 0.2 for 20% drawdown)
    """
    if equity.empty:
        return 0.0
    roll_max = equity.cummax()
    drawdown = (equity - roll_max) / roll_max
    return float(drawdown.min() * -1)


def cagr(equity: pd.Series) -> float:
    """Compute compound annual growth rate from equity series.

    Assumes equity index is datetime-like.
    """
    if equity.empty:
        return 0.0
    start_val = float(equity.iloc[0])
    end_val = float(equity.iloc[-1])
    start_date = pd.to_datetime(equity.index[0])
    end_date = pd.to_datetime(equity.index[-1])
    years = (end_date - start_date).days / 365.25
    if years <= 0:
        return 0.0
    return float((end_val / start_val) ** (1.0 / years) - 1.0)


def win_rate(trades: Iterable[dict]) -> float:
    """Compute win rate from an iterable of trades.

    Each trade dict must include 'pnl' (float) key.
    """
    trades_list = list(trades)
    if not trades_list:
        return 0.0
    wins = [1 for t in trades_list if float(t.get("pnl", 0.0)) > 0]
    return float(len(wins) / len(trades_list))


def profit_factor(trades: Iterable[dict]) -> float:
    """Compute profit factor = gross profit / gross loss.

    Returns large number for zero loss.
    """
    trades_list = list(trades)
    if not trades_list:
        return 0.0
    gross_profit = sum(t["pnl"] for t in trades_list if t["pnl"] > 0)
    gross_loss = -sum(t["pnl"] for t in trades_list if t["pnl"] < 0)
    if gross_loss == 0:
        return float("inf") if gross_profit > 0 else 0.0
    return float(gross_profit / gross_loss)


def trade_statistics(trades: Iterable[dict]) -> dict:
    """Summarize trade list into basic statistics.

    Returns:
        dict containing total_trades, wins, losses, win_rate, gross_profit,
        gross_loss, net_profit, avg_win, avg_loss, profit_factor
    """
    trades_list = list(trades)
    total = len(trades_list)
    if total == 0:
        return {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0,
            "gross_profit": 0.0,
            "gross_loss": 0.0,
            "net_profit": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "profit_factor": 0.0,
        }

    wins = [t for t in trades_list if t["pnl"] > 0]
    losses = [t for t in trades_list if t["pnl"] <= 0]
    gross_profit = sum(t["pnl"] for t in wins)
    gross_loss = -sum(t["pnl"] for t in losses)
    net = sum(t["pnl"] for t in trades_list)
    avg_win = float(np.mean([t["pnl"] for t in wins]) if wins else 0.0)
    avg_loss = float(np.mean([t["pnl"] for t in losses]) if losses else 0.0)

    return {
        "total_trades": total,
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": float(len(wins) / total),
        "gross_profit": float(gross_profit),
        "gross_loss": float(gross_loss),
        "net_profit": float(net),
        "avg_win": float(avg_win),
        "avg_loss": float(avg_loss),
        "profit_factor": profit_factor(trades_list),
    }
