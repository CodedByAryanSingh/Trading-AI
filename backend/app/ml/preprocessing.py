"""Feature engineering and data preprocessing."""
from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


class FeatureEngineer:
    """Engineer features from OHLCV data."""

    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_names: List[str] = []

    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create technical features from price data."""
        data = df.copy()

        # Price-based features
        data["returns"] = data["Close"].pct_change()
        data["log_returns"] = np.log(data["Close"] / data["Close"].shift(1))

        # Moving averages
        for window in [5, 10, 20, 50]:
            data[f"sma_{window}"] = data["Close"].rolling(window=window).mean()
            data[f"ema_{window}"] = data["Close"].ewm(span=window).mean()
            data[f"distance_sma_{window}"] = (data["Close"] - data[f"sma_{window}"]) / data[f"sma_{window}"]

        # Volatility
        data["volatility_20"] = data["returns"].rolling(window=20).std()
        data["atr_14"] = self._calculate_atr(data, 14)

        # Volume features
        data["volume_sma_20"] = data["Volume"].rolling(window=20).mean()
        data["volume_ratio"] = data["Volume"] / data["volume_sma_20"]

        # Price action
        data["body_size"] = abs(data["Close"] - data["Open"]) / data["Open"]
        data["upper_wick"] = (data["High"] - data[["Close", "Open"]].max(axis=1)) / data["Open"]
        data["lower_wick"] = (data[["Close", "Open"]].min(axis=1) - data["Low"]) / data["Open"]

        # Lag features
        for lag in [1, 2, 3, 5]:
            data[f"returns_lag_{lag}"] = data["returns"].shift(lag)

        self.feature_names = [c for c in data.columns if c not in ["Open", "High", "Low", "Close", "Volume"]]
        return data.dropna()

    def _calculate_atr(self, data: pd.DataFrame, window: int) -> pd.Series:
        """Calculate ATR."""
        high = data["High"]
        low = data["Low"]
        close = data["Close"]
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=window).mean()

    def prepare_train_data(
        self,
        df: pd.DataFrame,
        target_horizon: int = 5,
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare X, y arrays for training."""
        features_df = self.create_features(df)

        # Target: future return direction
        future_return = features_df["Close"].shift(-target_horizon) / features_df["Close"] - 1
        features_df["target"] = np.where(future_return > 0.01, 1, np.where(future_return < -0.01, -1, 0))

        features_df = features_df.dropna()

        X = features_df[self.feature_names].values
        y = features_df["target"].values

        X_scaled = self.scaler.fit_transform(X)
        return X_scaled, y, self.feature_names

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """Transform new data using fitted scaler."""
        features_df = self.create_features(df)
        X = features_df[self.feature_names].values
        return self.scaler.transform(X)
