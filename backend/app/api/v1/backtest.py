"""Backtesting endpoints."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.backtest.engine import BacktestEngine
from app.core.data_loader import DataLoader
from app.schemas import BacktestRequest, BacktestResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.post("/run", response_model=BacktestResponse)
async def run_backtest(req: BacktestRequest):
    try:
        loader = DataLoader()
        data_map = await loader.load_async([req.ticker], interval="1d", period=req.period)
        df = data_map.get(req.ticker)
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {req.ticker}")
        df = df.copy()
        df["signal"] = 0
        if req.strategy == "sma":
            df["sma_short"] = df["Close"].rolling(10).mean()
            df["sma_long"] = df["Close"].rolling(30).mean()
            df.loc[df["sma_short"] > df["sma_long"], "signal"] = 1
            df.loc[df["sma_short"] < df["sma_long"], "signal"] = -1
        elif req.strategy == "ema":
            df["ema_short"] = df["Close"].ewm(span=12).mean()
            df["ema_long"] = df["Close"].ewm(span=26).mean()
            df.loc[df["ema_short"] > df["ema_long"], "signal"] = 1
            df.loc[df["ema_short"] < df["ema_long"], "signal"] = -1
        elif req.strategy == "rsi":
            delta = df["Close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df["rsi"] = 100 - (100 / (1 + rs))
            df.loc[df["rsi"] < 30, "signal"] = 1
            df.loc[df["rsi"] > 70, "signal"] = -1
        engine = BacktestEngine(initial_cash=req.initial_cash)
        engine.run(df, signal_column="signal")
        trades = [{"entry_time": str(t.get("entry_time", "")),
                   "exit_time": str(t.get("exit_time", "")) if t.get("exit_time") else None,
                   "side": t.get("side", ""), "entry_price": float(t.get("entry_price", 0)),
                   "exit_price": float(t.get("exit_price", 0)) if t.get("exit_price") else None,
                   "pnl": float(t.get("pnl", 0)) if t.get("pnl") is not None else None}
                  for t in engine.trades]
        equity = engine.equity_dataframe().reset_index().to_dict(orient="records")
        return BacktestResponse(summary=engine.summary(), trades=trades, equity=equity)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Backtest failed: %s", exc)
        raise HTTPException(status_code=500, detail="Backtest execution failed")
