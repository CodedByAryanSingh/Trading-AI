"""Custom exceptions for Trading-AI."""
from __future__ import annotations

class TradingAIError(Exception): pass
class MarketDataError(TradingAIError): pass
class StrategyError(TradingAIError): pass
class AuthenticationError(TradingAIError): pass
class ValidationError(TradingAIError): pass
