import yfinance as yf
import pandas as pd


class MarketData:
    def __init__(self, symbol: str):
        self.symbol = symbol.upper()

    def get_historical_data(
        self,
        period: str = "1y",
        interval: str = "1d"
    ) -> pd.DataFrame:

        data = yf.download(
            self.symbol,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=True
        )

        if data.empty:
            raise ValueError(f"No data found for '{self.symbol}'")

        return data