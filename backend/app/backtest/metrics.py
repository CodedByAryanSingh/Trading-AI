"""Backtest performance metrics."""
from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd


def calculate_metrics(trades: List[Dict], equity_curve: pd.DataFrame) -> Dict[str, float]:
    """Calculate comprehensive performance metrics."""
    if equity_curve.empty:
        return {}

    returns = equity_curve["equity"].pct_change().dropna()

    metrics = {
        "total_return_pct": round((equity_curve["equity"].iloc[-1] / equity_curve["equity"].iloc[0] - 1) * 100, 2),
        "cagr_pct": 0.0,
        "volatility_annualized": round(returns.std() * np.sqrt(252) * 100, 2),
        "sharpe_ratio": 0.0,
        "sortino_ratio": 0.0,
        "max_drawdown_pct": 0.0,
        "calmar_ratio": 0.0,
        "win_rate_pct": 0.0,
        "profit_factor": 0.0,
        "avg_trade_return": 0.0,
    }

    if len(returns) > 0:
        metrics["sharpe_ratio"] = round((returns.mean() / returns.std()) * np.sqrt(252), 2) if returns.std() > 0 else 0

        downside_returns = returns[returns < 0]
        metrics["sortino_ratio"] = round((returns.mean() / downside_returns.std()) * np.sqrt(252), 2) if len(downside_returns) > 0 and downside_returns.std() > 0 else 0

    # Drawdown
    cummax = equity_curve["equity"].cummax()
    drawdown = (equity_curve["equity"] - cummax) / cummax
    metrics["max_drawdown_pct"] = round(drawdown.min() * 100, 2)

    # Trade metrics
    if trades:
        pnls = [t.get("pnl", 0) or 0 for t in trades]
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p <= 0]

        metrics["win_rate_pct"] = round(len(wins) / len(pnls) * 100, 2) if pnls else 0
        metrics["profit_factor"] = round(sum(wins) / abs(sum(losses)), 2) if losses and sum(losses) != 0 else float("inf")
        metrics["avg_trade_return"] = round(np.mean(pnls), 2) if pnls else 0

    return metrics
