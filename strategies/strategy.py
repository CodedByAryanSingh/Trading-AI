"""Compatibility shim for legacy strategies.strategy module.

This module exposes StrategyManager for backwards compatibility. The
monolithic StrategyEngine was refactored into modular strategy classes
under the strategies package. Importing StrategyEngine here returns a
thin wrapper around the StrategyManager for compatibility with older
call sites.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from .manager import StrategyManager


class StrategyEngine:
    """Backward-compatible wrapper around StrategyManager.

    Keeps a similar interface to the previous StrategyEngine with a single
    `multi_indicator_confirmation` method while encouraging use of the new
    manager and per-strategy classes.
    """

    def __init__(self, data: Any) -> None:
        self.manager = StrategyManager(data)
        self.manager.auto_register_defaults()

    def multi_indicator_confirmation(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Aggregate registered strategies and return the combined decision."""
        return self.manager.aggregate(threshold=(params or {}).get("decision_threshold", 0.2))


# Expose old-style name
StrategyError = Exception
