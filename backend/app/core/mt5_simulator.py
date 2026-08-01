"""MT5 simulator: provides a mock websocket stream that mimics MetaTrader5 tick and candle updates.
This is a simulated feed suitable for development and demos when a real MT5 terminal is not available.
"""
from __future__ import annotations
import asyncio
import random
import time
from typing import Dict, Any
from fastapi import WebSocket, WebSocketDisconnect


async def mt5_stream(websocket: WebSocket):
    await websocket.accept()
    params = websocket.query_params
    ticker = params.get("ticker", "EURUSD").upper()
    timeframe = params.get("tf", "1m")  # e.g., 1m,5m,1h

    # map timeframe to seconds
    tf_map = {"1m": 60, "5m": 300, "15m": 900, "1h": 3600, "4h": 14400, "1d": 86400}
    interval = tf_map.get(timeframe, 60)

    # Base price per symbol (pseudo-random but deterministic-ish)
    base_price = 1.1000 + (sum(ord(c) for c in ticker) % 100) / 10000.0

    # Current bar and tick
    now = int(time.time())
    current_bar = {
        "time": now,
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

            # handle incoming messages non-blocking
            try:
                if websocket.client_state.name == "CONNECTED":
                    # receive with short timeout
                    recv_task = asyncio.create_task(websocket.receive_text())
                    done, _ = await asyncio.wait({recv_task}, timeout=0, return_when=asyncio.ALL_COMPLETED)
                    if recv_task in done:
                        msg = recv_task.result()
                        # simple control messages: ping, set_ticker:EURUSD, set_tf:5m
                        if msg == "ping":
                            await websocket.send_json({"type": "pong"})
                        elif msg.startswith("set_ticker:"):
                            new_t = msg.split(":", 1)[1].upper()
                            ticker = new_t
                            # tweak base_price for new ticker
                            base_price = 1.0000 + (sum(ord(c) for c in ticker) % 100) / 10000.0
                            await websocket.send_json({"type": "info", "message": f"ticker set to {ticker}"})
                        elif msg.startswith("set_tf:"):
                            new_tf = msg.split(":", 1)[1]
                            interval = tf_map.get(new_tf, interval)
                            await websocket.send_json({"type": "info", "message": f"timeframe set to {new_tf}"})
            except asyncio.CancelledError:
                break
            except Exception:
                # ignore receive errors
                pass
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
