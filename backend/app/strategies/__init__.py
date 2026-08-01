"""Trading strategies package."""
from __future__ import annotations
from .base import Signal, Strategy, StrategyError
from .manager import StrategyManager
__all__ = ["Signal", "Strategy", "StrategyError", "StrategyManager"]
