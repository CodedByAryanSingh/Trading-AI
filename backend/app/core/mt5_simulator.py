"""MT5 websocket feed with an optional real MetaTrader 5 connector."""
from __future__ import annotations
import asyncio
import random
import time
from fastapi import WebSocket, WebSocketDisconnect
from app.config import settings


def _real_mt5():
    if not settings.mt5_enabled:
        return None
    try:
        import MetaTrader5 as mt5
    except ImportError:
        return None
    initialized = mt5.initialize(path=settings.mt5_path) if settings.mt5_path else mt5.initialize()
    if not initialized:
        return None
    if settings.mt5_login and settings.mt5_password and settings.mt5_server:
        if not mt5.login(settings.mt5_login, password=settings.mt5_password, server=settings.mt5_server):
            mt5.shutdown()
            return None
    return mt5


def _history(mt5, ticker: str, timeframe: str):
    if mt5 is None:
        return []
    timeframe_map = {
        "1m": mt5.TIMEFRAME_M1, "5m": mt5.TIMEFRAME_M5, "15m": mt5.TIMEFRAME_M15,
        "1h": mt5.TIMEFRAME_H1, "4h": mt5.TIMEFRAME_H4, "1d": mt5.TIMEFRAME_D1,
    }
    rates = mt5.copy_rates_from_pos(ticker, timeframe_map.get(timeframe, mt5.TIMEFRAME_M1), 0, 200)
    if rates is None:
        return []
    return [{"time": int(row["time"]), "open": float(row["open"]), "high": float(row["high"]),
             "low": float(row["low"]), "close": float(row["close"]), "volume": float(row["tick_volume"])}
            for row in rates]


async def mt5_stream(websocket: WebSocket):
    await websocket.accept()
    params = websocket.query_params
    ticker = params.get("ticker", "EURUSD").upper()
    timeframe = params.get("tf", "1m")  # e.g., 1m,5m,1h
    mt5 = await asyncio.to_thread(_real_mt5)

    if mt5:
        await websocket.send_json({"type": "status", "source": "mt5", "message": "Connected to MetaTrader 5"})
        history = await asyncio.to_thread(_history, mt5, ticker, timeframe)
        await websocket.send_json({"type": "history", "symbol": ticker, "candles": history})
        try:
            while True:
                await asyncio.sleep(1)
                tick = await asyncio.to_thread(mt5.symbol_info_tick, ticker)
                if tick is None:
                    await websocket.send_json({"type": "status", "source": "mt5", "message": f"Waiting for {ticker} market data"})
                    continue
                await websocket.send_json({"type": "tick", "symbol": ticker, "price": float(tick.last or tick.bid), "time": int(tick.time)})
        except WebSocketDisconnect:
            return
        finally:
            mt5.shutdown()
        return

    await websocket.send_json({"type": "status", "source": "simulator", "message": "MT5 terminal unavailable; using demo feed"})

    # map timeframe to seconds
    tf_map = {"1m": 60, "5m": 300, "15m": 900, "1h": 3600, "4h": 14400, "1d": 86400}
    interval = tf_map.get(timeframe, 60)

    # Base price per symbol (pseudo-random but deterministic-ish)
    base_price = 1.1000 + (sum(ord(c) for c in ticker) % 100) / 10000.0

    # Current bar and tick
    now = int(time.time())
    current_bar = {
        "time": now - (now % interval),
        "open": base_price,
        "high": base_price,
        "low": base_price,
        "close": base_price,
    }
    last_emit = time.time()

    try:
        while True:
            # simulate tick arrival every 0.5-1.5s
            await asyncio.sleep(random.uniform(0.5, 1.5))
            # small random walk
            delta = random.uniform(-0.0008, 0.0008)
            new_price = max(0.0001, current_bar["close"] + delta)
            # update current bar
            current_bar["high"] = max(current_bar["high"], new_price)
            current_bar["low"] = min(current_bar["low"], new_price)
            current_bar["close"] = new_price

            tick_msg = {
                "type": "tick",
                "symbol": ticker,
                "price": round(new_price, 5),
                "time": int(time.time()),
            }
            await websocket.send_json(tick_msg)

            # emit new candle when interval elapsed
            now_time = time.time()
            if now_time - last_emit >= interval:
                candle = {
                    "type": "candle",
                    "symbol": ticker,
                    "time": int(now_time),
                    "open": round(current_bar["open"], 5),
                    "high": round(current_bar["high"], 5),
                    "low": round(current_bar["low"], 5),
                    "close": round(current_bar["close"], 5),
                }
                await websocket.send_json(candle)
                # reset bar
                current_bar = {"time": int(now_time), "open": current_bar["close"], "high": current_bar["close"], "low": current_bar["close"], "close": current_bar["close"]}
                last_emit = now_time

    except WebSocketDisconnect:
        return
    except Exception:
        try:
            await websocket.close()
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
