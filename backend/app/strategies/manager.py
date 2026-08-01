"""Strategy manager to orchestrate multiple strategies."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import pandas as pd
from .base import Signal, Strategy
from .bollinger import BollingerStrategy
from .breakout import BreakoutStrategy
from .ema import EMAStrategy
from .ict import ICTStrategy
from .macd import MACDStrategy
from .rsi import RSIStrategy
from .smc import SMCStrategy
from .sma import SMAStrategy
from .trend import TrendStrategy
from app.utils.logger import get_logger

logger = get_logger(__name__)

class StrategyManager:
    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data.copy()
        self.strategies: List[Strategy] = []

    def register(self, strat: Strategy) -> None:
        self.strategies.append(strat)

    def auto_register_defaults(self, config: Optional[Dict[str, Any]] = None) -> None:
        cfg = config or {}
        self.strategies = [
            SMAStrategy(self.data, int(cfg.get("sma_short", 50)), int(cfg.get("sma_long", 200))),
            EMAStrategy(self.data, int(cfg.get("ema_short", 12)), int(cfg.get("ema_long", 26))),
            RSIStrategy(self.data, int(cfg.get("rsi_window", 14)), cfg.get("rsi_lower", 30), cfg.get("rsi_upper", 70)),
            MACDStrategy(self.data),
            BollingerStrategy(self.data, int(cfg.get("bb_window", 20)), cfg.get("bb_n_std", 2.0)),
            TrendStrategy(self.data),
            BreakoutStrategy(self.data),
            SMCStrategy(self.data),
            ICTStrategy(self.data),
        ]

    @staticmethod
    def _score_from_signal(signal: str) -> int:
        return {"BUY": 1, "SELL": -1}.get(signal, 0)

    def aggregate(self, threshold: float = 0.2) -> Dict[str, Any]:
        breakdown: List[Dict[str, Any]] = []
        weighted = 0.0
        weight_sum = 0.0
        for strat in self.strategies:
            try:
                sig = strat.generate()
                s_val = self._score_from_signal(sig.signal)
                conf = float(sig.confidence)
                breakdown.append({
                    "name": strat.__class__.__name__,
                    "signal": sig.signal,
                    "score": float(s_val),
                    "confidence": conf,
                    "details": sig.details,
                })
                weighted += s_val * conf
                weight_sum += conf
            except Exception as exc:
                logger.exception("Strategy %s failed", strat.__class__.__name__)
                breakdown.append({
                    "name": strat.__class__.__name__,
                    "signal": "HOLD",
                    "score": 0.0,
                    "confidence": 0.0,
                    "details": {"error": str(exc)},
                })
        final_score = (weighted / weight_sum) if weight_sum > 0 else 0.0
        final_signal = "BUY" if final_score > threshold else ("SELL" if final_score < -threshold else "HOLD")
        return {"signal": final_signal, "confidence": float(min(1.0, abs(final_score))),
                "score": float(final_score), "breakdown": breakdown}
