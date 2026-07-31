"""Base strategy classes and types.

Defines a Signal dataclass and an abstract Strategy base class that other
strategy implementations inherit from. All strategies return a Signal via
generate().
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any, Dict

import pandas as pd

from utils.logger import get_logger

logger = get_logger(__name__)


class StrategyError(Exception):
    """Exception raised for strategy-specific errors."""


@dataclass
class Signal:
    """Unified signal representation returned by strategies.

    Attributes:
        signal: One of 'BUY', 'SELL', 'HOLD'.
        confidence: Float between 0.0 and 1.0.
        details: Extra diagnostic values useful for explanation or testing.
    """

    signal: str
    confidence: float
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable dict representation."""
        d = asdict(self)
        # Ensure primitive types
        d["confidence"] = float(d.get("confidence", 0.0))
        return d


class Strategy(ABC):
    """Abstract strategy base class.

    Implementations must be side-effect free and unit-testable. The
    constructor receives a pandas DataFrame (price data) and an optional
    configuration.
    """

    def __init__(self, data: pd.DataFrame):
        if not isinstance(data, pd.DataFrame):
            raise StrategyError("data must be a pandas DataFrame")
        self.data = data.copy()

    @abstractmethod
    def generate(self) -> Signal:
        """Generate a trading signal for the latest available bar.

        Returns:
            Signal dataclass describing decision and confidence.
        """
        raise NotImplementedError
