"""Backtesting engine package."""
from __future__ import annotations

from .engine import BacktestEngine
from .metrics import calculate_metrics
from .report import generate_report

__all__ = ["BacktestEngine", "calculate_metrics", "generate_report"]
