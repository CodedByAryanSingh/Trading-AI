"""
FastAPI application entrypoint for Trading-AI.

Run with: python -m api.main or `uvicorn api.main:app --reload` for local
development. The app exposes /analyze which is implemented in routes.py.
"""
from __future__ import annotations

import uvicorn
from fastapi import FastAPI

from api.routes import router as api_router
from utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(title="Trading-AI API", version="0.1.0")

# Enable CORS for local frontend development
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

# include authentication routes
from api.auth import router as auth_router
app.include_router(auth_router, prefix="/api/auth")


@app.get("/healthz")
async def healthz() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}


# WebSocket endpoint for mock intraday OHLCV streaming used by frontend for development/testing.
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import random
from data.data_loader import DataLoader


@app.websocket("/ws/ohlcv")
async def websocket_ohlcv(websocket: WebSocket):
    """WebSocket that streams mock intraday OHLCV updates for a ticker.

    Query parameters (from the client's WebSocket URL):
    - ticker: required, e.g. AAPL
    - interval: e.g. 1m, 5m, 1h

    Sends JSON messages of the form:
    - { type: 'update', candle: {...}, volume: {...} }  -- update current bar
    - { type: 'new', candle: {...}, volume: {...} }     -- new bar completed/appended
    """
    await websocket.accept()
    params = websocket.query_params
    ticker = params.get("ticker") or params.get("symbol") or "AAPL"
    interval = params.get("interval") or "1m"

    # map interval to seconds for simulation
    interval_map = {"1m": 60, "5m": 300, "15m": 900, "1h": 3600, "4h": 14400}
    interval_seconds = interval_map.get(interval, 60)

    dl = DataLoader()
    try:
        # try to get a recent historical candle to seed the mock stream
        data_map = dl.load([ticker], interval=interval, period="1d")
        df = data_map.get(ticker)
        if df is None or df.empty:
            raise RuntimeError("no historical data")
        last = df.iloc[-1]
        # use timezone-naive timestamp seconds
        last_ts = int(last.name.to_pydatetime().timestamp())
        open_p = float(last.get("Open", last.get("open", last.get("Close", 100))))
        high_p = float(last.get("High", open_p))
        low_p = float(last.get("Low", open_p))
        close_p = float(last.get("Close", open_p))
        vol = float(last.get("Volume", 0.0))
    except Exception:
        # fallback seed values
        last_ts = int(asyncio.get_event_loop().time())
        open_p = 100.0
        high_p = 100.0
        low_p = 100.0
        close_p = 100.0
        vol = 0.0

    current_bar = {
        "time": last_ts,
        "open": open_p,
        "high": high_p,
        "low": low_p,
        "close": close_p,
    }
    current_vol = {"time": last_ts, "value": vol}

    start_time = asyncio.get_event_loop().time()
    last_emit = start_time

    try:
        while True:
            # simulate a small tick every second
            await asyncio.sleep(1)
            now = asyncio.get_event_loop().time()
            # small random walk
            delta = random.uniform(-0.2, 0.2)
            new_close = max(0.01, current_bar["close"] + delta)
            current_bar["high"] = max(current_bar["high"], new_close)
            current_bar["low"] = min(current_bar["low"], new_close)
            current_bar["close"] = new_close
            # increase volume randomly
            current_vol["value"] = current_vol.get("value", 0) + random.randint(1, 100)

            # send update for current bar
            msg = {"type": "update", "candle": current_bar, "volume": current_vol}
            await websocket.send_json(msg)

            # if interval elapsed, finalize bar and start new one
            if now - last_emit >= interval_seconds:
                # send 'new' event to append the finalized bar
                await websocket.send_json({"type": "new", "candle": current_bar, "volume": current_vol})
                # advance timestamp by interval_seconds
                current_bar = {
                    "time": int(current_bar["time"] + interval_seconds),
                    "open": current_bar["close"],
                    "high": current_bar["close"],
                    "low": current_bar["close"],
                    "close": current_bar["close"],
                }
                current_vol = {"time": current_bar["time"], "value": 0}
                last_emit = now
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for %s@%s", ticker, interval)
    except Exception as exc:
        logger.exception("WebSocket error for %s@%s: %s", ticker, interval, exc)
        try:
            await websocket.close()
        except Exception:
            pass


if __name__ == "__main__":
    logger.info("Starting Trading-AI API")
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)
