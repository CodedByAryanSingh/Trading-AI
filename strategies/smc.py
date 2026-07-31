"""SMC-based strategy wrapper using indicators.smc.SMCDetector."""
from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from .base import Signal, Strategy, StrategyError
from indicators.smc import SMCDetector
from utils.logger import get_logger

logger = get_logger(__name__)


class SMCStrategy(Strategy):
    """Simple SMC strategy using Break of Structure (BOS) and CHoCH detection.

    This is a lightweight wrapper around the SMCDetector. It produces a
    BUY when recent structure is bullish (BOS up), SELL when bearish, else HOLD.
    """

    def __init__(self, data: pd.DataFrame) -> None:
        super().__init__(data)
        self.detector = SMCDetector(self.data)

    def generate(self) -> Signal:
        try:
            bos = self.detector.detect_bos()
            choch = self.detector.detect_choch()
            details: Dict[str, Any] = {"bos": bos, "choch": choch}
            # Conservative rules: require BOS to be present for directional signal
            if bos is None and choch is None:
                return Signal(signal="HOLD", confidence=0.0, details=details)
            # if BOS indicates bullish structure
            if bos == "bullish" or choch == "bullish":
                return Signal(signal="BUY", confidence=0.7, details=details)
            if bos == "bearish" or choch == "bearish":
                return Signal(signal="SELL", confidence=0.7, details=details)
            return Signal(signal="HOLD", confidence=0.0, details=details)
        except Exception as exc:
            logger.exception("SMCStrategy failed: %s", exc)
            raise StrategyError("SMCStrategy computation failed")
