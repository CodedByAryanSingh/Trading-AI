"""
Backtest engine implementation.

Provides BacktestEngine with features:
- Buy/Sell simulation
- Portfolio balance and cash management
- Single active position (long-only) with position tracking
- Stop loss and take profit per trade
- Commission per trade
- Equity curve recording
- Performance metrics (total return, CAGR, max drawdown, sharpe, win rate, profit factor)

Design notes:
- Strategy is provided as a callable that accepts (bt, timestamp, row) and returns a dict:
    {'signal': 'BUY'|'SELL'|'HOLD', 'size': float (fraction of capital or absolute shares),
     'stop_loss': optional (price or pct, see docs), 'take_profit': optional (price or pct)}
- By default size is treated as fraction when 0 < size <= 1, otherwise as absolute shares.
- Only one position is tracked at a time (simpler single-instrument backtest). Extending to multiple positions is straightforward.

"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

import math
import numpy as np
import pandas as pd


@dataclass
class Position:
    entry_time: pd.Timestamp
    entry_price: float
    size: int
    direction: str  # 'LONG' or 'SHORT' (we'll implement LONG primarily)
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    commission: float = 0.0
    exit_time: Optional[pd.Timestamp] = None
    exit_price: Optional[float] = None
    pnl: Optional[float] = None


class BacktestEngine:
    """Simple but feature-complete single-instrument backtest engine.

    Args:
        data: pd.DataFrame with a DateTimeIndex and at least a 'Close' column.
        initial_capital: starting cash balance.
        commission: flat commission per trade (applied on entry and exit).
        slippage: per-share slippage to subtract from fills (positive number means worse fill price for the trader).
        allow_short: whether to allow shorting (not thoroughly tested here; focused on long flow).
    """

    def __init__(
        self,
        data: pd.DataFrame,
        initial_capital: float = 10000.0,
        commission: float = 0.0,
        slippage: float = 0.0,
        allow_short: bool = False,
    ): 
        if not isinstance(data, pd.DataFrame):
            raise TypeError("data must be a pandas DataFrame")
        if "Close" not in data.columns:
            raise ValueError("data must contain a 'Close' column")

        self.data = data.copy()
        self.initial_capital = float(initial_capital)
        self.cash = float(initial_capital)
        self.commission = float(commission)
        self.slippage = float(slippage)
        self.allow_short = bool(allow_short)

        self.position: Optional[Position] = None
        self.trades: List[Dict[str, Any]] = []
        self.equity_curve: pd.Series = pd.Series(dtype=float)
        self._equity_list: List[float] = []
        self._index_list: List[pd.Timestamp] = []

    def _fill_buy(self, timestamp: pd.Timestamp, price: float, size: int) -> None:
        """Execute a buy at given price for size shares (assumes no existing position)."""
        total_cost = price * size
        c = self.commission
        if self.cash < total_cost + c:
            # cannot afford full size; adjust down
            max_size = int((self.cash - c) // price)
            if max_size <= 0:
                return
            size = max_size
            total_cost = price * size
        self.cash -= (total_cost + c)
        self.position = Position(entry_time=timestamp, entry_price=price, size=size, direction="LONG", commission=c)

    def _close_position(self, timestamp: pd.Timestamp, price: float) -> None:
        """Close current position at given price and record trade."""
        if self.position is None:
            return
        pos = self.position
        proceeds = price * pos.size
        c = self.commission
        self.cash += (proceeds - c)
        pnl = (price - pos.entry_price) * pos.size if pos.direction == "LONG" else (pos.entry_price - price) * pos.size
        pos.exit_time = timestamp
        pos.exit_price = price
        pos.pnl = pnl - (pos.commission + c)  # subtract both entry and exit commission

        self.trades.append({
            "entry_time": pos.entry_time,
            "exit_time": pos.exit_time,
            "entry_price": pos.entry_price,
            "exit_price": pos.exit_price,
            "size": pos.size,
            "direction": pos.direction,
            "pnl": pos.pnl,
            "commission": pos.commission + c,
        })
        self.position = None

    def _mark_to_market(self, price: float, timestamp: pd.Timestamp) -> float:
        """Return current equity = cash + mark-to-market position value."""
        pos_val = 0.0
        if self.position is not None:
            pos = self.position
            if pos.direction == "LONG":
                pos_val = price * pos.size
            else:
                # short: value = (entry - current) * size + initial cash was adjusted earlier
                pos_val = (pos.entry_price - price) * pos.size + (pos.entry_price * pos.size)
        equity = self.cash + pos_val
        # record
        self._equity_list.append(float(equity))
        self._index_list.append(timestamp)
        return equity

    def run(self, strategy: Callable[["BacktestEngine", pd.Timestamp, pd.Series], Dict[str, Any]], 
            size: float = 0.1) -> None:
        """Run the backtest over the provided data.

        strategy: callable that receives (engine, timestamp, row) and returns a dict with keys:
            - 'signal': 'BUY' | 'SELL' | 'HOLD'
            - optional 'size': fraction (0-1) or absolute shares
            - optional 'stop_loss': either a price (float) or a negative percent like -0.05 meaning 5% below entry
            - optional 'take_profit': price or positive percent like 0.05 meaning 5% above entry

        size argument is default trade size fraction of capital if strategy doesn't provide.
        """
        if not callable(strategy):
            raise TypeError("strategy must be callable")

        for idx, row in self.data.iterrows():
            price = float(row["Close"])
            timestamp = pd.Timestamp(idx)

            # check stop loss / take profit first (use today's close as fill)
            if self.position is not None:
                pos = self.position
                # stop loss: if price <= stop for LONG
                triggered = False
                if pos.stop_loss is not None:
                    if pos.direction == "LONG" and price <= pos.stop_loss:
                        self._close_position(timestamp, max(price - self.slippage, 0.0))
                        triggered = True
                    elif pos.direction == "SHORT" and price >= pos.stop_loss:
                        self._close_position(timestamp, min(price + self.slippage, price))
                        triggered = True
                if not triggered and pos.take_profit is not None:
                    if pos.direction == "LONG" and price >= pos.take_profit:
                        self._close_position(timestamp, max(price - self.slippage, 0.0))
                        triggered = True
                    elif pos.direction == "SHORT" and price <= pos.take_profit:
                        self._close_position(timestamp, min(price + self.slippage, price))
                        triggered = True

            # get strategy signal
            try:
                sig = strategy(self, timestamp, row) or {}
            except TypeError:
                # strategy might accept only data row
                sig = strategy(timestamp, row) or {}

            signal = sig.get("signal", "HOLD")
            requested_size = sig.get("size", size)
            stop = sig.get("stop_loss")
            tp = sig.get("take_profit")

            # Entry logic: only allow entry if no existing position; simple long-only flow
            if signal == "BUY" and self.position is None:
                # determine fill price after slippage
                fill_price = max(price + self.slippage, 0.0)
                # compute shares
                shares = 0
                if 0 < requested_size <= 1:
                    # fraction of available cash
                    allocate = self.cash * float(requested_size)
                    shares = int((allocate - self.commission) // fill_price)
                else:
                    # absolute shares requested
                    shares = int(requested_size)
                if shares > 0:
                    self._fill_buy(timestamp, fill_price, shares)
                    # set stops relative to entry
                    if self.position is not None:
                        entry_p = self.position.entry_price
                        # interpret stop/tp as percent if absolute seems like a fraction
                        if isinstance(stop, (int, float)):
                            if abs(stop) < 1:  # treat as percent
                                # negative percent means below entry
                                self.position.stop_loss = entry_p * (1 + float(stop))
                            else:
                                self.position.stop_loss = float(stop)
                        if isinstance(tp, (int, float)):
                            if abs(tp) < 1:
                                self.position.take_profit = entry_p * (1 + float(tp))
                            else:
                                self.position.take_profit = float(tp)

            # Exit logic on explicit SELL signal
            if signal == "SELL" and self.position is not None:
                fill_price = max(price - self.slippage, 0.0)
                self._close_position(timestamp, fill_price)

            # record equity at the end of the bar
            self._mark_to_market(price, timestamp)

        # at end, if still open, close at last price
        if self.position is not None:
            last_price = float(self.data.iloc[-1]["Close"])
            self._close_position(self.data.index[-1], last_price)
            # mark final equity
            self._mark_to_market(last_price, self.data.index[-1])

        # build equity curve series
        if self._index_list:
            self.equity_curve = pd.Series(data=self._equity_list, index=pd.DatetimeIndex(self._index_list))
        else:
            self.equity_curve = pd.Series(dtype=float)

    def compute_metrics(self, periods_per_year: Optional[int] = None) -> Dict[str, Any]:
        """Compute a set of standard performance metrics from the equity curve and trades.

        Returns a dict with keys: total_return, annualized_return (CAGR), sharpe, max_drawdown, num_trades, win_rate, profit_factor
        """
        if self.equity_curve.empty:
            return {}

        # returns
        equity = self.equity_curve.fillna(method="ffill")
        rets = equity.pct_change().dropna()

        total_return = (equity.iloc[-1] / equity.iloc[0]) - 1.0

        # guess periods_per_year from index frequency when not provided
        if periods_per_year is None:
            inferred = pd.infer_freq(self.equity_curve.index)
            if inferred is None:
                # fallback to daily
                periods_per_year = 252
            elif inferred.upper().startswith("D"):
                periods_per_year = 252
            elif inferred.upper().startswith("H"):
                periods_per_year = 252 * 24
            elif inferred.upper().startswith("T") or inferred.upper().startswith("MIN"):
                periods_per_year = 252 * 6.5 * 60
            else:
                periods_per_year = 252

        # CAGR
        num_periods = len(equity)
        years = num_periods / float(periods_per_year) if periods_per_year > 0 else 1.0
        if years > 0:
            cagr = (equity.iloc[-1] / equity.iloc[0]) ** (1.0 / years) - 1.0
        else:
            cagr = float("nan")

        # Sharpe (assume risk-free ~ 0)
        if rets.std() > 0:
            sharpe = (rets.mean() / rets.std()) * math.sqrt(periods_per_year)
        else:
            sharpe = float("nan")

        # Max drawdown
        roll_max = equity.cummax()
        drawdown = (equity - roll_max) / roll_max
        max_dd = float(drawdown.min())

        # Trades stats
        num_trades = len(self.trades)
        wins = [t["pnl"] for t in self.trades if t["pnl"] is not None and t["pnl"] > 0]
        losses = [t["pnl"] for t in self.trades if t["pnl"] is not None and t["pnl"] <= 0]
        win_rate = (len(wins) / num_trades) if num_trades > 0 else float("nan")
        gross_win = sum(wins) if wins else 0.0
        gross_loss = -sum([x for x in losses]) if losses else 0.0
        profit_factor = (gross_win / gross_loss) if gross_loss > 0 else (float("inf") if gross_win > 0 else float("nan"))

        return {
            "total_return": float(total_return),
            "cagr": float(cagr),
            "sharpe": float(sharpe) if not math.isnan(sharpe) else None,
            "max_drawdown": float(max_dd),
            "num_trades": int(num_trades),
            "win_rate": float(win_rate) if not math.isnan(win_rate) else None,
            "profit_factor": float(profit_factor) if not (isinstance(profit_factor, float) and math.isinf(profit_factor)) else float("inf"),
        }


# Lightweight example strategy helper for tests and examples
def sma_crossover_strategy_factory(short: int = 20, long: int = 50, size: float = 0.1):
    """Return a strategy callable that uses SMA crossover on 'Close' to produce BUY/SELL signals.

    The inner callable matches the (engine, timestamp, row) signature.
    """
    def strategy(engine: BacktestEngine, timestamp: pd.Timestamp, row: pd.Series) -> Dict[str, Any]:
        # Ensure indicators are available on engine.data
        df = engine.data
        if f"SMA_{short}" not in df.columns or f"SMA_{long}" not in df.columns:
            # compute quickly
            df[f"SMA_{short}"] = df["Close"].rolling(window=short, min_periods=1).mean()
            df[f"SMA_{long}"] = df["Close"].rolling(window=long, min_periods=1).mean()
            engine.data = df

        cur = engine.data.loc[timestamp]
        s = cur[f"SMA_{short}"]
        l = cur[f"SMA_{long}"]
        if s > l:
            return {"signal": "BUY", "size": size}
        elif s < l:
            return {"signal": "SELL", "size": size}
        return {"signal": "HOLD"}

    return strategy
