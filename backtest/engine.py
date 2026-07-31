"""Backtesting engine.

Provides BacktestEngine class that simulates buy/sell signals over historical
price data and tracks portfolio equity, positions, commissions, stop-loss,
and take-profit rules. Designed to be simple, extensible, and unit-testable.

Features implemented:
- Buy/Sell simulation
- Portfolio balance and equity curve
- Position tracking
- Stop loss and take profit (percentage-based)
- Commission (percentage or fixed)
- Trade history
- Exportable equity curve and trades

Notes:
- This engine is intentionally conservative and deterministic. It trades on
  bar-close prices and checks stop/take conditions on each bar's high/low
  to simulate intrabar exits.
- Position sizing is specified as fraction of equity to allocate per trade.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import math
import pandas as pd

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Position:
    """Simple position representation.

    Attributes:
        side: 'long' or 'short'
        entry_price: price filled
        size: number of units (shares/coins)
        entry_time: index or timestamp when opened
        stop_price: optional stop loss price
        take_price: optional take profit price
    """

    side: str
    entry_price: float
    size: int
    entry_time: object
    stop_price: Optional[float] = None
    take_price: Optional[float] = None


class BacktestEngineError(Exception):
    """Custom exception for backtest errors."""


class BacktestEngine:
    """A straightforward backtesting engine for discrete bar data.

    Example:
        engine = BacktestEngine(initial_cash=100000)
        engine.run(df, signal_column='signal')
        eq = engine.equity_curve()
        trades = engine.trades

    The engine expects a pandas DataFrame with a datetime index and at
    minimum a 'Open','High','Low','Close' column. Signals can be provided
    in a column with values: 1 (buy/open long), -1 (sell/short or close), 0 hold.
    Alternatively strings 'BUY'/'SELL' are supported.
    """

    def __init__(
        self,
        initial_cash: float = 100_000.0,
        commission: float = 0.0,
        fixed_commission: float = 0.0,
        position_size: float = 0.1,
        allow_short: bool = False,
    ) -> None:
        """Initialize engine.

        Args:
            initial_cash: starting cash in account
            commission: proportional commission per trade (e.g. 0.001 = 0.1%)
            fixed_commission: flat commission per trade
            position_size: fraction of equity to allocate per new trade (0-1)
            allow_short: whether short positions are allowed
        """
        self.initial_cash = float(initial_cash)
        self.cash = float(initial_cash)
        self.commission = float(commission)
        self.fixed_commission = float(fixed_commission)
        self.position_size = float(position_size)
        if not (0.0 < self.position_size <= 1.0):
            raise BacktestEngineError("position_size must be in (0, 1]")
        self.allow_short = bool(allow_short)

        self.position: Optional[Position] = None
        self.trades: List[Dict] = []
        # equity history entries: list of tuples (timestamp, equity, cash, position_value)
        self._history: List[Tuple] = []

    def reset(self) -> None:
        """Reset engine state to initial conditions (preserve config)."""
        self.cash = float(self.initial_cash)
        self.position = None
        self.trades = []
        self._history = []

    def _calc_fees(self, trade_value: float) -> float:
        """Calculate fees for a trade (proportional + fixed)."""
        return abs(trade_value) * self.commission + self.fixed_commission

    def _open_long(self, price: float, timestamp: object, frac: float) -> None:
        # determine allocation from current equity
        equity = self._current_equity(price)
        allocate = equity * frac
        size = math.floor(allocate / price)
        if size <= 0:
            logger.debug("Not enough equity to open any shares at price %s", price)
            return
        cost = size * price
        fees = self._calc_fees(cost)
        total_cost = cost + fees
        if total_cost > self.cash:
            # adjust size down to fit cash
            size = math.floor((self.cash - self.fixed_commission) / (price * (1 + self.commission)))
            if size <= 0:
                logger.debug("Insufficient cash after fees to open position")
                return
            cost = size * price
            fees = self._calc_fees(cost)
            total_cost = cost + fees
        self.cash -= total_cost
        self.position = Position(side="long", entry_price=price, size=size, entry_time=timestamp)
        logger.debug("Opened LONG size=%s entry=%.5f fees=%.5f cash_remaining=%.2f", size, price, fees, self.cash)

    def _close_position(self, price: float, timestamp: object) -> None:
        if self.position is None:
            return
        pos = self.position
        if pos.side == "long":
            proceeds = pos.size * price
            fees = self._calc_fees(proceeds)
            self.cash += proceeds - fees
            pnl = (price - pos.entry_price) * pos.size - fees - (pos.entry_price * pos.size * 0 if False else 0)
        else:  # short
            # For short, buy back the position
            cost_to_buy = pos.size * price
            fees = self._calc_fees(cost_to_buy)
            # when short opened we didn't track proceeds separately in this simple model; assume cash increased when opening short
            # PnL = initial_proceeds - cost_to_buy - fees
            pnl = (pos.entry_price - price) * pos.size - fees
            self.cash += (pos.entry_price * pos.size) - cost_to_buy - fees
        trade = {
            "entry_time": pos.entry_time,
            "exit_time": timestamp,
            "side": pos.side,
            "entry_price": pos.entry_price,
            "exit_price": price,
            "size": pos.size,
            "pnl": round(pnl, 8),
            "fees": round(float(self._calc_fees(pos.entry_price * pos.size) + self._calc_fees(price * pos.size)) / 2.0, 8),
        }
        self.trades.append(trade)
        logger.debug("Closed %s at %.5f size=%s pnl=%.5f cash=%.2f", pos.side, price, pos.size, pnl, self.cash)
        self.position = None

    def _current_position_value(self, market_price: float) -> float:
        if self.position is None:
            return 0.0
        if self.position.side == "long":
            return float(self.position.size * market_price)
        # short position value represented as negative exposure
        return float(-self.position.size * market_price)

    def _current_equity(self, market_price: float) -> float:
        return float(self.cash + self._current_position_value(market_price))

    def run(
        self,
        data: pd.DataFrame,
        signal_column: str = "signal",
        price_column: str = "Close",
        stop_loss_pct: Optional[float] = None,
        take_profit_pct: Optional[float] = None,
        position_size: Optional[float] = None,
    ) -> None:
        """Run backtest on provided data.

        Args:
            data: pandas DataFrame indexed by datetime with OHLC columns.
            signal_column: column containing -1/0/1 or 'BUY'/'SELL'
            price_column: which price to use for fills (default 'Close')
            stop_loss_pct: optional stop loss percentage (e.g. 0.02 for 2%)
            take_profit_pct: optional take profit percentage
            position_size: override engine position_size for this run (fraction)
        """
        if position_size is not None:
            if not (0.0 < position_size <= 1.0):
                raise BacktestEngineError("position_size must be in (0,1]")
            run_frac = float(position_size)
        else:
            run_frac = float(self.position_size)

        required_cols = {"Open", "High", "Low", "Close"}
        if not required_cols.issubset(set(data.columns)):
            raise BacktestEngineError(f"Data must include columns: {required_cols}")

        self.reset()

        for idx, row in data.iterrows():
            high = float(row.get("High"))
            low = float(row.get("Low"))
            close = float(row.get(price_column))
            sig = row.get(signal_column, 0)
            # normalize signal
            if isinstance(sig, str):
                sig_val = 1 if str(sig).upper() in ("BUY", "LONG") else -1 if str(sig).upper() in ("SELL", "SHORT") else 0
            else:
                try:
                    sig_val = int(sig)
                except Exception:
                    sig_val = 0

            # check existing position for stop / take intrabar using high/low
            if self.position is not None:
                pos = self.position
                closed_by_rule = False
                # long stop: low <= stop_price triggers
                if pos.side == "long" and pos.stop_price is not None and low <= pos.stop_price:
                    # close at stop_price
                    self._close_position(pos.stop_price, idx)
                    closed_by_rule = True
                # long take profit: high >= take_price
                elif pos.side == "long" and pos.take_price is not None and high >= pos.take_price:
                    self._close_position(pos.take_price, idx)
                    closed_by_rule = True
                # short rules (reverse)
                elif pos.side == "short" and pos.stop_price is not None and high >= pos.stop_price:
                    self._close_position(pos.stop_price, idx)
                    closed_by_rule = True
                elif pos.side == "short" and pos.take_price is not None and low <= pos.take_price:
                    self._close_position(pos.take_price, idx)
                    closed_by_rule = True

                if closed_by_rule:
                    # after automatic close do not process new signal on same bar
                    self._history.append((idx, self._current_equity(close), self.cash, 0.0 if self.position is None else self._current_position_value(close)))
                    continue

            # process signals
            if sig_val == 1:
                # BUY signal
                if self.position is None:
                    # open long
                    self._open_long(close, idx, run_frac)
                    # set stop/take
                    if self.position is not None and stop_loss_pct is not None:
                        self.position.stop_price = round(self.position.entry_price * (1.0 - float(stop_loss_pct)), 8)
                    if self.position is not None and take_profit_pct is not None:
                        self.position.take_price = round(self.position.entry_price * (1.0 + float(take_profit_pct)), 8)
                else:
                    # if short and allow_short True then closing short
                    if self.position.side == "short":
                        self._close_position(close, idx)
            elif sig_val == -1:
                # SELL signal
                if self.position is None:
                    if self.allow_short:
                        # open short (not implemented fully in sizing complexity)
                        # For simplicity, mirror long logic but mark side as 'short'
                        equity = self._current_equity(close)
                        allocate = equity * run_frac
                        size = math.floor(allocate / close)
                        if size > 0:
                            # assume we receive proceeds = size * price when opening short
                            proceeds = size * close
                            fees = self._calc_fees(proceeds)
                            self.cash += proceeds - fees
                            self.position = Position(side="short", entry_price=close, size=size, entry_time=idx)
                            if stop_loss_pct is not None:
                                # for short a stop loss is above entry
                                self.position.stop_price = round(self.position.entry_price * (1.0 + float(stop_loss_pct)), 8)
                            if take_profit_pct is not None:
                                self.position.take_price = round(self.position.entry_price * (1.0 - float(take_profit_pct)), 8)
                            logger.debug("Opened SHORT size=%s at %.5f", size, close)
                else:
                    # close long
                    if self.position.side == "long":
                        self._close_position(close, idx)

            # record equity at close of bar
            equity = self._current_equity(close)
            pos_val = self._current_position_value(close)
            self._history.append((idx, equity, self.cash, pos_val))

    def equity_curve(self) -> pd.Series:
        """Return equity curve as pandas Series indexed by timestamps."""
        if not self._history:
            return pd.Series(dtype=float)
        df = pd.DataFrame(self._history, columns=["time", "equity", "cash", "position_value"]).set_index("time")
        return df["equity"]

    def equity_dataframe(self) -> pd.DataFrame:
        """Return full equity history DataFrame with cash and position_value."""
        if not self._history:
            return pd.DataFrame()
        df = pd.DataFrame(self._history, columns=["time", "equity", "cash", "position_value"]).set_index("time")
        return df

    def summary(self) -> Dict:
        """Return a compact summary of the run including final cash and trades."""
        eq = self.equity_curve()
        return {
            "start_cash": self.initial_cash,
            "end_cash": round(self.cash, 8),
            "final_equity": float(eq.iloc[-1]) if not eq.empty else float(self.cash),
            "n_trades": len(self.trades),
        }
