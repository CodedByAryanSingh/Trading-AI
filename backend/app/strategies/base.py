"""Base strategy classes and types."""
from __future__ import annotations
from abc import ABC
from dataclasses import asdict, dataclass
from typing import Any, Dict
import pandas as pd

class StrategyError(Exception): pass

@dataclass
class Signal:
    signal: str
    confidence: float
    details: Dict[str, Any]
    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["confidence"] = float(d.get("confidence", 0.0))
        return d

class Strategy(ABC):
    def __init__(self, data: pd.DataFrame):
        if not isinstance(data, pd.DataFrame):
            raise StrategyError("data must be a pandas DataFrame")
        self.data = data.copy()
    def generate(self) -> Signal:
        raise NotImplementedError("Strategies must implement generate()")
