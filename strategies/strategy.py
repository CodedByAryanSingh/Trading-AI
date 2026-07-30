"""
StrategyEngine module (object-oriented).

Provides StrategyEngine which wraps technical indicator computations and
exposes methods that return consistent signals and confidence scores for
SMA/EMA/RSI/MACD/Bollinger strategies as well as a multi-indicator
aggregator for confirmation across indicators.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd

from indicators.technical import TechnicalIndicators
from utils.logger import get_logger

logger = get_logger(__name__)


class StrategyError(Exception):
    """Custom exception for strategy-related errors."""


class StrategyEngine:
    """Engine to compute strategy signals and confidence scores.

    The engine operates on a pandas DataFrame with at least a 'Close'
    column and optionally 'High', 'Low', and 'Volume'. It uses the
    TechnicalIndicators helper to compute indicators in a testable, modular
    way. All methods return plain Python types or DataFrames and avoid
    side effects on inputs.
    """

    def __init__(self, data: pd.DataFrame):
        """Initialize the StrategyEngine.

        Args:
            data: Price DataFrame with index of timestamps and columns
                  ['Open','High','Low','Close','Volume'] where available.
        """
        if not isinstance(data, pd.DataFrame):
            raise StrategyError("data must be a pandas DataFrame")
        self._raw = data.copy()
        self.ind = TechnicalIndicators(self._raw)

    def sma_signal(self, short: int = 50, long: int = 200, price_col: str = "Close") -> Dict[str, Any]:
        """Compute SMA crossover signal for the latest row.

        Returns a dict: {'signal': 'BUY'|'SELL'|'HOLD', 'confidence': float, 'short': float, 'long': float}
        """
        df = self.ind.add_sma(short, price_col).to_frame(name=f"SMA_{short}")
        # add long SMA on the same underlying data
        base = self.ind.data.copy()
        base[f"SMA_{short}"] = self.ind.data[f"SMA_{short}"]
        base[f"SMA_{long}"] = self.ind.add_sma(long, price_col)

        last = base.dropna(subset=[price_col, f"SMA_{short}", f"SMA_{long}"]).iloc[-1]
        s = float(last[f"SMA_{short}"])
        l = float(last[f"SMA_{long}"])
        price = float(last[price_col])
        signal = "BUY" if s > l else ("SELL" if s < l else "HOLD")
        confidence = min(1.0, abs(s - l) / (price if price != 0 else 1.0))
        return {"signal": signal, "confidence": float(confidence), "short": s, "long": l}

    def ema_signal(self, short: int = 12, long: int = 26, price_col: str = "Close") -> Dict[str, Any]:
        """Compute EMA crossover latest signal and confidence."""
        self.ind.add_ema(short, price_col)
        self.ind.add_ema(long, price_col)
        last = self.ind.data.dropna(subset=[price_col, f"EMA_{short}", f"EMA_{long}"]).iloc[-1]
        s = float(last[f"EMA_{short}"])
        l = float(last[f"EMA_{long}"])
        price = float(last[price_col])
        signal = "BUY" if s > l else ("SELL" if s < l else "HOLD")
        confidence = min(1.0, abs(s - l) / (price if price != 0 else 1.0))
        return {"signal": signal, "confidence": float(confidence), "short": s, "long": l}

    def rsi_signal(self, window: int = 14, lower: int = 30, upper: int = 70, price_col: str = "Close") -> Dict[str, Any]:
        """Compute RSI-based signal: oversold -> BUY, overbought -> SELL."""
        self.ind.add_rsi(window, price_col)
        last = self.ind.data.dropna(subset=[f"RSI_{window}"]).iloc[-1]
        rsi = float(last[f"RSI_{window}"])
        if rsi < lower:
            signal = "BUY"
        elif rsi > upper:
            signal = "SELL"
        else:
            signal = "HOLD"
        # confidence proportional to distance from threshold
        if signal == "BUY":
            confidence = min(1.0, (lower - rsi) / (lower if lower != 0 else 1.0))
        elif signal == "SELL":
            confidence = min(1.0, (rsi - upper) / (100 - upper if (100 - upper) != 0 else 1.0))
        else:
            confidence = 0.0
        return {"signal": signal, "confidence": float(confidence), "rsi": rsi}

    def macd_signal(self, price_col: str = "Close") -> Dict[str, Any]:
        """Compute MACD crossover signal and simple histogram-based confidence."""
        self.ind.add_macd(price_col)
        last = self.ind.data.dropna(subset=["MACD", "MACD_Signal", "MACD_Histogram"]).iloc[-1]
        macd = float(last["MACD"])
        macd_sig = float(last["MACD_Signal"])
        hist = float(last["MACD_Histogram"])
        signal = "BUY" if macd > macd_sig else ("SELL" if macd < macd_sig else "HOLD")
        price = float(last[price_col])
        confidence = min(1.0, abs(hist) / (price if price != 0 else 1.0))
        return {"signal": signal, "confidence": float(confidence), "macd": macd, "signal_line": macd_sig, "hist": hist}

    def bollinger_signal(self, window: int = 20, n_std: float = 2.0, price_col: str = "Close") -> Dict[str, Any]:
        """Bollinger band signal: price below lower -> BUY, above upper -> SELL."""
        self.ind.add_bollinger(window, n_std, price_col)
        last = self.ind.data.dropna(subset=["BB_High", "BB_Low", "BB_Middle"]).iloc[-1]
        price = float(last[price_col])
        lower = float(last["BB_Low"])
        upper = float(last["BB_High"])
        if price < lower:
            signal = "BUY"
        elif price > upper:
            signal = "SELL"
        else:
            signal = "HOLD"
        # confidence increases the further price is outside bands
        if signal == "BUY":
            confidence = min(1.0, (lower - price) / (price if price != 0 else 1.0))
        elif signal == "SELL":
            confidence = min(1.0, (price - upper) / (price if price != 0 else 1.0))
        else:
            # small confidence based on band width
            confidence = min(1.0, (upper - lower) / (price * 10 if price != 0 else 1.0))
        return {"signal": signal, "confidence": float(abs(confidence)), "lower": lower, "upper": upper, "price": price}

    def multi_indicator_confirmation(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run multiple indicators and produce an aggregated decision.

        The method computes each indicator's discrete signal mapped to +1/-1/0
        and weights them by their confidence. The final score is the
        weighted average; a decision threshold maps the score to BUY/SELL/HOLD.
        """
        params = params or {}
        breakdown = []

        try:
            sma = self.sma_signal(params.get("sma_short", 50), params.get("sma_long", 200))
            ema = self.ema_signal(params.get("ema_short", 12), params.get("ema_long", 26))
            rsi = self.rsi_signal(params.get("rsi_window", 14), params.get("rsi_lower", 30), params.get("rsi_upper", 70))
            macd = self.macd_signal()
            bb = self.bollinger_signal(params.get("bb_window", 20), params.get("bb_n_std", 2.0))
        except Exception as exc:
            logger.exception("Failed to compute indicators: %s", exc)
            raise StrategyError("Indicator computation failed")

        mapping = {"BUY": 1, "SELL": -1, "HOLD": 0}
        items = [("SMA", sma), ("EMA", ema), ("RSI", rsi), ("MACD", macd), ("BB", bb)]

        weighted = 0.0
        weight_sum = 0.0
        for name, res in items:
            sig_val = mapping.get(res["signal"], 0)
            conf = float(res.get("confidence", 0.0))
            breakdown.append({"name": name, "signal": res["signal"], "score": sig_val, "confidence": conf})
            weighted += sig_val * conf
            weight_sum += conf

        final_score = (weighted / weight_sum) if weight_sum > 0 else 0.0
        threshold = float(params.get("decision_threshold", 0.2))
        final_signal = "BUY" if final_score > threshold else ("SELL" if final_score < -threshold else "HOLD")
        overall_confidence = min(1.0, abs(final_score))

        return {"signal": final_signal, "confidence": float(overall_confidence), "score": float(final_score), "breakdown": breakdown}
