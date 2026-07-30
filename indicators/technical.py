import pandas as pd
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands


class TechnicalIndicators:
    def __init__(self, data: pd.DataFrame):
         self.data = data
    def add_indicators(self) -> pd.DataFrame:
        close = self.data["Close"]

        # Moving Averages
        self.data["SMA_20"] = SMAIndicator(close, window=20).sma_indicator()
        self.data["SMA_50"] = SMAIndicator(close, window=50).sma_indicator()

        # Exponential Moving Average
        self.data["EMA_20"] = EMAIndicator(close, window=20).ema_indicator()

        # RSI
        self.data["RSI"] = RSIIndicator(close, window=14).rsi()

        # MACD
        macd = MACD(close)

        self.data["MACD"] = macd.macd()
        self.data["MACD_Signal"] = macd.macd_signal()
        self.data["MACD_Histogram"] = macd.macd_diff()

        # Bollinger Bands
        bb = BollingerBands(close)

        self.data["BB_High"] = bb.bollinger_hband()
        self.data["BB_Low"] = bb.bollinger_lband()
        self.data["BB_Middle"] = bb.bollinger_mavg()

        return self.data