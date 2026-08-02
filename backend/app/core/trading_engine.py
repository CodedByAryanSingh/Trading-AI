"""Risk-gated trading ideas and an in-memory paper execution ledger."""
from __future__ import annotations

from datetime import datetime, timezone
from itertools import count
from typing import Any

import numpy as np
import pandas as pd

from app.indicators.technical import calculate_atr
from app.schemas import PaperOrderRequest, TradeIdeaRequest
from app.strategies.manager import StrategyManager


def _value(frame: pd.DataFrame, column: str) -> float:
    value = frame[column].iloc[-1]
    if isinstance(value, pd.Series):
        value = value.iloc[0]
    return float(value)


def _json_value(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def build_trade_idea(data: pd.DataFrame, request: TradeIdeaRequest, account_value: float = 100_000) -> dict[str, Any]:
    """Create a rule-based trade plan from the ensemble; HOLD is the safe default."""
    manager = StrategyManager(data)
    manager.auto_register_defaults()
    result = manager.aggregate(threshold=0.25)
    entry_price = _value(data, "Close")
    atr_series = calculate_atr(data).dropna()
    atr = float(atr_series.iloc[-1]) if not atr_series.empty else entry_price * 0.01
    risk_distance = max(atr * 1.5, entry_price * 0.002)
    confidence = round(float(result["confidence"]), 4)
    risk_amount = round(account_value * request.risk_percent, 2)
    reasons = [f"{item['name']} {item['signal'].lower()}" for item in result["breakdown"] if item["signal"] != "HOLD"]
    action = result["signal"]
    status = "ready"
    data_source = str(data.attrs.get("data_source", "provider"))

    if data_source != "provider":
        action = "HOLD"
        status = "waiting"
        reasons = ["Provider data is unavailable; demo data cannot create a trade recommendation"]
    elif action == "HOLD":
        status = "waiting"
        reasons = reasons or ["No multi-strategy alignment"]
    elif confidence < 0.55:
        action = "HOLD"
        status = "waiting"
        reasons.append("Confidence is below the 55% execution threshold")

    stop_loss = take_profit = risk_reward = None
    suggested_quantity = 0.0
    if action == "BUY":
        stop_loss = round(entry_price - risk_distance, 6)
        take_profit = round(entry_price + (risk_distance * 2), 6)
    elif action == "SELL":
        stop_loss = round(entry_price + risk_distance, 6)
        take_profit = round(entry_price - (risk_distance * 2), 6)
    if stop_loss is not None and take_profit is not None:
        suggested_quantity = round(risk_amount / abs(entry_price - stop_loss), 4)
        risk_reward = 2.0
        reasons.insert(0, "Risk is capped at 1–2% of paper capital")

    breakdown = [
        {"name": item["name"], "signal": item["signal"], "confidence": item["confidence"],
         "score": int(item["score"]), "details": _json_value(item["details"])}
        for item in result["breakdown"]
    ]
    return {
        "ticker": request.ticker.upper(), "action": action, "confidence": confidence,
        "entry_price": round(entry_price, 6), "stop_loss": stop_loss, "take_profit": take_profit,
        "risk_reward": risk_reward, "suggested_quantity": suggested_quantity, "risk_amount": risk_amount,
        "status": status, "data_source": data_source, "reasons": reasons, "strategy_breakdown": breakdown,
    }


class PaperTradingBook:
    """Small deterministic paper ledger; it never communicates with a broker."""

    def __init__(self, starting_cash: float = 100_000) -> None:
        self.starting_cash = starting_cash
        self.orders: list[dict[str, Any]] = []
        self._ids = count(1)

    def submit(self, request: PaperOrderRequest) -> dict[str, Any]:
        risk_per_unit = abs(request.entry_price - request.stop_loss)
        if risk_per_unit == 0:
            raise ValueError("Stop loss must differ from the entry price")
        if request.side == "BUY" and request.take_profit <= request.entry_price:
            raise ValueError("Buy target must be above entry")
        if request.side == "SELL" and request.take_profit >= request.entry_price:
            raise ValueError("Sell target must be below entry")
        risk_amount = round(self.starting_cash * request.risk_percent, 2)
        order = {
            "id": next(self._ids), "mode": "paper", "ticker": request.ticker.upper(), "side": request.side,
            "quantity": round(risk_amount / risk_per_unit, 4), "entry_price": request.entry_price,
            "stop_loss": request.stop_loss, "take_profit": request.take_profit, "risk_amount": risk_amount,
            "status": "open", "created_at": datetime.now(timezone.utc),
        }
        self.orders.append(order)
        return order

    def snapshot(self) -> dict[str, Any]:
        reserved_risk = round(sum(order["risk_amount"] for order in self.orders if order["status"] == "open"), 2)
        return {
            "mode": "paper", "starting_cash": self.starting_cash,
            "available_cash": round(self.starting_cash - reserved_risk, 2),
            "reserved_risk": reserved_risk, "open_orders": self.orders,
        }


paper_book = PaperTradingBook()
