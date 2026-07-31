"""Strategies package

This package contains modular, testable strategy implementations.
Each strategy exposes a class with a `generate` method that returns a
consistent Signal dataclass (signal, confidence, details).

Import the manager to run multi-strategy aggregation.
"""
from .manager import StrategyManager  # noqa: F401

__all__ = ["StrategyManager"]
