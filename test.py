from data.market_data import MarketData
from indicators.technical import TechnicalIndicators

print("📈 Fetching market data...")

market = MarketData("AAPL")
data = market.get_historical_data()

print("✅ Market data downloaded.")

print("📊 Calculating technical indicators...")

technical = TechnicalIndicators(data)
data = technical.add_indicators()

print("✅ Technical indicators calculated.\n")

print(
    data[
        [
            "SMA_20",
            "SMA_50",
            "EMA_20",
            "RSI",
            "MACD",
            "MACD_Signal",
            "MACD_Histogram",
            "BB_High",
            "BB_Low",
            "BB_Middle",
        ]
    ].tail()
)