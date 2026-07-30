"""
Technical indicators module.

Provides an object-oriented wrapper around common technical indicators.
The implementation leverages the `ta` library where appropriate and
falls back to pandas-based implementations when necessary. All methods
are instance methods that add columns to the internal DataFrame and
return them for convenience.
"""
from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd
from ta.momentum import RSIIndicator, StochRSIIndicator
from ta.trend import EMAIndicator, SMAIndicator, MACD
from ta.volatility import BollingerBands, KeltnerChannel
from ta.volume import OnBalanceVolumeIndicator, MFIIndicator

from utils.logger import get_logger

logger = get_logger(__name__)


class TechnicalIndicators:
    """Compute a suite of technical indicators on OHLCV data.

    The class is instantiated with a DataFrame containing at minimum a
    'Close' column and optionally 'High', 'Low', and 'Volume'. Methods add
    indicator columns to a copy of the DataFrame and return that DataFrame.
    """

    def __init__(self, data: pd.DataFrame):
        """Initialize with a DataFrame of price data.

        Args:
            data: DataFrame with columns ['Open','High','Low','Close','Volume'] ideally.
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError("data must be a pandas DataFrame")
        self.data = data.copy()

    @staticmethod
    def _ensure_series(series: pd.Series) -> pd.Series:
        if isinstance(series, pd.DataFrame):
            return series.squeeze()
        return series

    def add_sma(self, window: int = 20, price_col: str = "Close") -> pd.Series:
        """Add Simple Moving Average (SMA) to the DataFrame."""
        s = self._ensure_series(self.data[price_col])
        self.data[f"SMA_{window}"] = s.rolling(window=window, min_periods=1).mean()
        return self.data[f"SMA_{window}"]

    def add_ema(self, window: int = 20, price_col: str = "Close") -> pd.Series:
        """Add Exponential Moving Average (EMA) to the DataFrame."""
        s = self._ensure_series(self.data[price_col])
        self.data[f"EMA_{window}"] = EMAIndicator(close=s, window=window).ema_indicator()
        return self.data[f"EMA_{window}"]

    def add_wma(self, window: int = 20, price_col: str = "Close") -> pd.Series:
        """Weighted Moving Average implemented via rolling apply."""
        s = self._ensure_series(self.data[price_col])

        def _wma(x: pd.Series) -> float:
            weights = np.arange(1, len(x) + 1)
            return float((x * weights).sum() / weights.sum())

        self.data[f"WMA_{window}"] = s.rolling(window=window, min_periods=1).apply(_wma, raw=False)
        return self.data[f"WMA_{window}"]

    def add_hma(self, window: int = 20, price_col: str = "Close") -> pd.Series:
        """Hull Moving Average (HMA) implementation."""
        s = self._ensure_series(self.data[price_col])
        half_length = int(window / 2)
        sqrt_length = int(np.sqrt(window))
        wma_half = s.rolling(window=half_length, min_periods=1).apply(lambda x: (x * np.arange(1, len(x) + 1)).sum() / np.arange(1, len(x) + 1).sum(), raw=False)
        wma_full = s.rolling(window=window, min_periods=1).apply(lambda x: (x * np.arange(1, len(x) + 1)).sum() / np.arange(1, len(x) + 1).sum(), raw=False)
        hma = (2 * wma_half) - wma_full
        self.data[f"HMA_{window}"] = hma.rolling(window=sqrt_length, min_periods=1).mean()
        return self.data[f"HMA_{window}"]

    def add_rsi(self, window: int = 14, price_col: str = "Close") -> pd.Series:
        """Add Relative Strength Index (RSI)."""
        s = self._ensure_series(self.data[price_col])
        self.data[f"RSI_{window}"] = RSIIndicator(close=s, window=window).rsi()
        return self.data[f"RSI_{window}"]

    def add_macd(self, price_col: str = "Close") -> pd.DataFrame:
        """Add MACD line, signal and histogram."""
        s = self._ensure_series(self.data[price_col])
        macd = MACD(close=s)
        self.data["MACD"] = macd.macd()
        self.data["MACD_Signal"] = macd.macd_signal()
        self.data["MACD_Histogram"] = macd.macd_diff()
        return self.data[["MACD", "MACD_Signal", "MACD_Histogram"]]

    def add_bollinger(self, window: int = 20, n_std: float = 2.0, price_col: str = "Close") -> pd.DataFrame:
        """Add Bollinger Bands (upper, middle, lower)."""
        s = self._ensure_series(self.data[price_col])
        bb = BollingerBands(close=s, window=window, window_dev=n_std)
        self.data["BB_High"] = bb.bollinger_hband()
        self.data["BB_Low"] = bb.bollinger_lband()
        self.data["BB_Middle"] = bb.bollinger_mavg()
        return self.data[["BB_High", "BB_Middle", "BB_Low"]]

    def add_keltner(self, window: int = 20, price_col: str = "Close") -> pd.DataFrame:
        """Add Keltner Channel (uses ta KeltnerChannel)."""
        try:
            s = self._ensure_series(self.data[price_col])
            kc = KeltnerChannel(high=self.data.get("High"), low=self.data.get("Low"), close=s, window=window)
            self.data["KC_High"] = kc.keltner_channel_hband()
            self.data["KC_Low"] = kc.keltner_channel_lband()
            self.data["KC_Mid"] = kc.keltner_channel_mband()
            return self.data[["KC_High", "KC_Mid", "KC_Low"]]
        except Exception:
            logger.exception("Failed to compute Keltner Channel")
            raise

    def add_obv(self, price_col: str = "Close", volume_col: str = "Volume") -> pd.Series:
        """Add On-Balance Volume indicator."""
        vol = self.data.get(volume_col)
        s = self._ensure_series(self.data[price_col])
        obv = OnBalanceVolumeIndicator(close=s, volume=vol)
        self.data["OBV"] = obv.on_balance_volume()
        return self.data["OBV"]

    def add_vwap(self, price_col: str = "Close", volume_col: str = "Volume") -> pd.Series:
        """Add Volume Weighted Average Price (VWAP).

        This implementation calculates a rolling VWAP across the available
        series; for session VWAP a separate session-aware implementation is
        recommended.
        """
        s = self._ensure_series(self.data[price_col])
        vol = self.data.get(volume_col)
        pv = s * vol
        vwap = pv.cumsum() / vol.cumsum()
        self.data["VWAP"] = vwap
        return self.data["VWAP"]

    def add_mfi(self, window: int = 14) -> pd.Series:
        """Add Money Flow Index (MFI) using ta library."""
        try:
            mfi = MFIIndicator(high=self.data.get("High"), low=self.data.get("Low"), close=self.data.get("Close"), volume=self.data.get("Volume"), window=window)
            self.data[f"MFI_{window}"] = mfi.money_flow_index()
            return self.data[f"MFI_{window}"]
        except Exception:
            logger.exception("Failed to compute MFI")
            raise

    def add_stoch_rsi(self, window: int = 14, smooth1: int = 3, smooth2: int = 3, price_col: str = "Close") -> pd.DataFrame:
        """Add Stochastic RSI (fastK, fastD)."""
        s = self._ensure_series(self.data[price_col])
        stoch = StochRSIIndicator(close=s, window=window, smooth1=smooth1, smooth2=smooth2)
        self.data["STOCH_RSI_K"] = stoch.stochrsi_k()
        self.data["STOCH_RSI_D"] = stoch.stochrsi_d()
        return self.data[["STOCH_RSI_K", "STOCH_RSI_D"]]

    def add_rsi_and_macd_and_bollinger(self) -> pd.DataFrame:
        """Convenience helper adding common trio indicators used in strategies."""
        self.add_rsi()
        self.add_macd()
        self.add_bollinger()
        return self.data

    def add_all(self) -> pd.DataFrame:
        """Run a reasonable subset of indicators for the core implementation."""
        # Price-based
        self.add_sma(20)
        self.add_sma(50)
        self.add_ema(20)
        self.add_wma(20)
        self.add_hma(20)

        # Momentum/oscillators
        self.add_rsi(14)
        self.add_stoch_rsi(14)
        self.add_macd()

        # Volatility/volume
        self.add_bollinger(20)
        self.add_keltner(20)
        self.add_obv()
        self.add_vwap()
        self.add_mfi(14)

        return self.data
