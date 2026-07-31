"""Strategy manager to orchestrate multiple strategies and aggregate signals."""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple

from .base import Signal, Strategy
from .sma import SMAStrategy
from .ema import EMAStrategy
from .rsi import RSIStrategy
from .macd import MACDStrategy
from .bollinger import BollingerStrategy
from .trend import TrendStrategy
from .breakout import BreakoutStrategy
from .smc import SMCStrategy
from .ict import ICTStrategy
from utils.logger import get_logger

import pandas as pd

logger = get_logger(__name__)


class StrategyManager:
    """Manage and run multiple strategy instances and aggregate their signals.

    Usage:
        mgr = StrategyManager(data)
        mgr.register(SMAStrategy(...))
        result = mgr.aggregate()
    """

    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data.copy()
        self.strategies: List[Strategy] = []

    def register(self, strat: Strategy) -> None:
        """Register a strategy instance to be included in aggregation."""
        self.strategies.append(strat)

    def auto_register_defaults(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Register a sensible default set of strategies.

        The config dict can customize parameters per-strategy.
        """
        cfg = config or {}
        self.strategies = [
            SMAStrategy(self.data, cfg.get("sma_short", 50), cfg.get("sma_long", 200)),
            EMAStrategy(self.data, cfg.get("ema_short", 12), cfg.get("ema_long", 26)),
            RSIStrategy(self.data, cfg.get("rsi_window", 14), cfg.get("rsi_lower", 30), cfg.get("rsi_upper", 70)),
            MACDStrategy(self.data),
            BollingerStrategy(self.data, cfg.get("bb_window", 20), cfg.get("bb_n_std", 2.0)),
            TrendStrategy(self.data),
            BreakoutStrategy(self.data),
            SMCStrategy(self.data),
            ICTStrategy(self.data),
        ]

    @staticmethod
    def _score_from_signal(signal: str) -> int:
        return {"BUY": 1, "SELL": -1}.get(signal, 0)

    def aggregate(self, threshold: float = 0.2) -> Dict[str, Any]:
        """Run all registered strategies and produce an aggregated result.

        Returns a dict containing final signal, confidence, aggregated score,
        and per-strategy breakdown for explainability.
        """
        breakdown: List[Dict[str, Any]] = []
        weighted = 0.0
        weight_sum = 0.0

        for strat in self.strategies:
            try:
                sig = strat.generate()
                s_val = self._score_from_signal(sig.signal)
                conf = float(sig.confidence)
                breakdown.append({"name": strat.__class__.__name__, "signal": sig.signal, "confidence": conf, "details": sig.details})
                weighted += s_val * conf
                weight_sum += conf
            except Exception as exc:  # keep manager robust
                logger.exception("Strategy %s failed: %s", strat.__class__.__name__, exc)
                breakdown.append({"name": strat.__class__.__name__, "signal": "HOLD", "confidence": 0.0, "details": {"error": str(exc)}})

        final_score = (weighted / weight_sum) if weight_sum > 0 else 0.0
        final_signal = "BUY" if final_score > threshold else ("SELL" if final_score < -threshold else "HOLD")
        overall_confidence = min(1.0, abs(final_score))

        return {"signal": final_signal, "confidence": float(overall_confidence), "score": float(final_score), "breakdown": breakdown}
