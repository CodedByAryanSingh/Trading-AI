"""Event-driven backtest engine."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd


@dataclass
class Trade:
    """Represents a single trade."""
    entry_time: datetime
    exit_time: Optional[datetime] = None
    side: str = "LONG"
    entry_price: float = 0.0
    exit_price: Optional[float] = None
    quantity: int = 1
    pnl: Optional[float] = None
    exit_reason: Optional[str] = None


class BacktestEngine:
    """Simple vectorized backtest engine."""

    def __init__(self, initial_cash: float = 100000.0, commission: float = 0.001):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.commission = commission
        self.position = 0
        self.trades: List[Dict[str, Any]] = []
        self.equity_curve: List[Dict[str, Any]] = []
        self.current_trade: Optional[Trade] = None

    def run(self, data: pd.DataFrame, signal_column: str = "signal") -> None:
        """Run backtest on provided data."""
        if signal_column not in data.columns:
            raise ValueError(f"Signal column {signal_column} not found in data")

        signals = data[signal_column].values
        prices = data["Close"].values
        times = data.index if isinstance(data.index, pd.DatetimeIndex) else pd.RangeIndex(len(data))

        for i in range(len(data)):
            price = float(prices[i])
            time = times[i]
            signal = int(signals[i])

            # Record equity
            equity = self.cash + (self.position * price)
            self.equity_curve.append({
                "time": str(time),
                "equity": equity,
                "cash": self.cash,
                "position": self.position,
            })

            # Open long
            if signal == 1 and self.position <= 0:
                if self.current_trade and self.current_trade.side == "SHORT":
                    self._close_trade(time, price, "signal_flip")
                self._open_trade(time, price, "LONG")

            # Open short
            elif signal == -1 and self.position >= 0:
                if self.current_trade and self.current_trade.side == "LONG":
                    self._close_trade(time, price, "signal_flip")
                self._open_trade(time, price, "SHORT")

            # Close on signal neutral
            elif signal == 0 and self.position != 0:
                self._close_trade(time, price, "neutral_signal")

    def _open_trade(self, time: Any, price: float, side: str) -> None:
        """Open a new trade."""
        qty = int(self.cash / (price * (1 + self.commission)))
        if qty <= 0:
            return

        cost = qty * price * (1 + self.commission)
        self.cash -= cost
        self.position = qty if side == "LONG" else -qty

        self.current_trade = Trade(
            entry_time=time if isinstance(time, datetime) else datetime.now(),
            side=side,
            entry_price=price,
            quantity=qty,
        )

    def _close_trade(self, time: Any, price: float, reason: str) -> None:
        """Close current trade."""
        if not self.current_trade:
            return

        qty = abs(self.position)
        if self.position > 0:
            proceeds = qty * price * (1 - self.commission)
            pnl = proceeds - (qty * self.current_trade.entry_price)
        else:
            proceeds = qty * self.current_trade.entry_price * 2 - (qty * price * (1 + self.commission))
            pnl = (qty * self.current_trade.entry_price) - (qty * price)

        self.cash += proceeds if self.position > 0 else (self.cash + proceeds)
        self.position = 0

        self.current_trade.exit_time = time if isinstance(time, datetime) else datetime.now()
        self.current_trade.exit_price = price
        self.current_trade.pnl = pnl
        self.current_trade.exit_reason = reason

        self.trades.append({
            "entry_time": self.current_trade.entry_time,
            "exit_time": self.current_trade.exit_time,
            "side": self.current_trade.side,
            "entry_price": self.current_trade.entry_price,
            "exit_price": self.current_trade.exit_price,
            "quantity": self.current_trade.quantity,
            "pnl": self.current_trade.pnl,
            "exit_reason": self.current_trade.exit_reason,
        })

        self.current_trade = None

    def summary(self) -> Dict[str, float]:
        """Generate backtest summary statistics."""
        if not self.equity_curve:
            return {}

        equity_df = pd.DataFrame(self.equity_curve)
        returns = equity_df["equity"].pct_change().dropna()

        total_return = (equity_df["equity"].iloc[-1] - self.initial_cash) / self.initial_cash

        winning_trades = [t for t in self.trades if t.get("pnl", 0) > 0]
        losing_trades = [t for t in self.trades if t.get("pnl", 0) <= 0]

        total_trades = len(self.trades)
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0

        avg_win = sum(t["pnl"] for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t["pnl"] for t in losing_trades) / len(losing_trades) if losing_trades else 0

        profit_factor = (
            sum(t["pnl"] for t in winning_trades) / abs(sum(t["pnl"] for t in losing_trades))
            if losing_trades and sum(t["pnl"] for t in losing_trades) != 0 else float("inf")
        )

        # Max drawdown
        cummax = equity_df["equity"].cummax()
        drawdown = (equity_df["equity"] - cummax) / cummax
        max_drawdown = drawdown.min()

        # Sharpe ratio (annualized, assuming daily data)
        sharpe = (returns.mean() / returns.std()) * (252 ** 0.5) if returns.std() != 0 else 0

        return {
            "total_return": round(total_return * 100, 2),
            "total_trades": total_trades,
            "win_rate": round(win_rate * 100, 2),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "profit_factor": round(profit_factor, 2),
            "max_drawdown": round(max_drawdown * 100, 2),
            "sharpe_ratio": round(sharpe, 2),
            "final_equity": round(equity_df["equity"].iloc[-1], 2),
        }

    def equity_dataframe(self) -> pd.DataFrame:
        """Return equity curve as DataFrame."""
        return pd.DataFrame(self.equity_curve)
