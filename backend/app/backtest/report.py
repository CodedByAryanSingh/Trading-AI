"""Backtest report generation."""
from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd

from .metrics import calculate_metrics


def generate_report(trades: List[Dict[str, Any]], equity_curve: pd.DataFrame) -> Dict[str, Any]:
    """Generate a comprehensive backtest report."""
    metrics = calculate_metrics(trades, equity_curve)

    trade_df = pd.DataFrame(trades) if trades else pd.DataFrame()

    report = {
        "summary": metrics,
        "trades": trades,
        "equity": equity_curve.reset_index().to_dict(orient="records"),
        "trade_statistics": {},
    }

    if not trade_df.empty and "pnl" in trade_df.columns:
        report["trade_statistics"] = {
            "best_trade": round(trade_df["pnl"].max(), 2),
            "worst_trade": round(trade_df["pnl"].min(), 2),
            "avg_trade": round(trade_df["pnl"].mean(), 2),
            "median_trade": round(trade_df["pnl"].median(), 2),
            "std_dev": round(trade_df["pnl"].std(), 2),
        }

    return report
