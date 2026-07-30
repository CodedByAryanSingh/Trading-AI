import pandas as pd
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands


class TechnicalIndicators:
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()

    def add_indicators(self) -> pd.DataFrame:
        """
        Adds common technical indicators to the market data.
        """

        # Handle yfinance MultiIndex columns
        close = self.data["Close"]

        if isinstance(close, pd.DataFrame):
            close = close.squeeze()

        # Simple Moving Averages
        self.data["SMA_20"] = SMAIndicator(close=close, window=20).sma_indicator()
        self.data["SMA_50"] = SMAIndicator(close=close, window=50).sma_indicator()

        # Exponential Moving Average
        self.data["EMA_20"] = EMAIndicator(close=close, window=20).ema_indicator()

        # Relative Strength Index
        self.data["RSI"] = RSIIndicator(close=close, window=14).rsi()

        # MACD
        macd = MACD(close=close)

        self.data["MACD"] = macd.macd()
        self.data["MACD_Signal"] = macd.macd_signal()
        self.data["MACD_Histogram"] = macd.macd_diff()

        # Bollinger Bands
        bb = BollingerBands(close=close)

        self.data["BB_High"] = bb.bollinger_hband()
        self.data["BB_Low"] = bb.bollinger_lband()
        self.data["BB_Middle"] = bb.bollinger_mavg()

        return self.data