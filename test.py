from data.market_data import MarketData
from indicators.technical import TechnicalIndicators
from src.preprocessing import DataPreprocessor

print("📈 Fetching market data...")

# Download stock data
stock = MarketData("AAPL")
data = stock.get_historical_data()

print(data.columns)
print(type(data["Close"]))
print(data.columns)
print(data["Close"])
print(type(data["Close"]))

print("✅ Market data downloaded.")

print("📊 Calculating technical indicators...")

# Add indicators
technical = TechnicalIndicators(data)
data = technical.add_indicators()

print("✅ Technical indicators added.")

print("🧹 Preprocessing data...")

# Clean data
preprocessor = DataPreprocessor(data)
data = preprocessor.preprocess()

print("✅ Data preprocessing completed.")

print("\nFinal Dataset Preview:\n")
print(data.head())

print("\nDataset Shape:", data.shape)
print("\nColumns:")
print(list(data.columns))