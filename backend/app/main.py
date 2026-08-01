"""FastAPI application entrypoint."""
from __future__ import annotations
import asyncio
import random
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, market, analysis, backtest, predictions, portfolio
from app.config import settings
from app.db import close_db, init_db
from app.utils.logger import get_logger

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Trading-AI API...")
    await init_db()
    yield
    logger.info("Shutting down Trading-AI API...")
    await close_db()

app = FastAPI(title=settings.app_name, version=settings.app_version,
              description="AI-Powered Quantitative Trading Intelligence Platform", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(auth.router,        prefix="/api/v1/auth",        tags=["Authentication"])
app.include_router(market.router,      prefix="/api/v1/market",      tags=["Market Data"])
app.include_router(analysis.router,    prefix="/api/v1/analysis",    tags=["Analysis"])
app.include_router(backtest.router,    prefix="/api/v1/backtest",    tags=["Backtesting"])
app.include_router(predictions.router, prefix="/api/v1/predictions", tags=["Predictions"])
app.include_router(portfolio.router,   prefix="/api/v1/portfolio",   tags=["Portfolio"])

@app.get("/healthz", tags=["Health"])
async def health_check() -> dict:
    return {"status": "ok", "version": settings.app_version}

@app.websocket("/ws/ohlcv")
async def websocket_ohlcv(websocket: WebSocket):
    """Stream mock OHLCV data for real-time chart updates."""
    await websocket.accept()
    params = websocket.query_params
    ticker = params.get("ticker", "AAPL")
    interval = params.get("interval", "1m")
    interval_map = {"1m": 60, "5m": 300, "15m": 900, "1h": 3600, "4h": 14400}
    interval_seconds = interval_map.get(interval, 60)
    base_price = random.uniform(50, 500)
    current_bar = {"time": int(asyncio.get_event_loop().time()), "open": base_price,
                   "high": base_price, "low": base_price, "close": base_price}
    current_vol = {"time": current_bar["time"], "value": 0.0}
    last_emit = asyncio.get_event_loop().time()
    try:
        while True:
            await asyncio.sleep(1)
            now = asyncio.get_event_loop().time()
            delta = random.uniform(-0.2, 0.2)
            new_close = max(0.01, current_bar["close"] + delta)
            current_bar["high"] = max(current_bar["high"], new_close)
            current_bar["low"] = min(current_bar["low"], new_close)
            current_bar["close"] = new_close
            current_vol["value"] += random.randint(1, 100)
            await websocket.send_json({"type": "update", "candle": current_bar, "volume": current_vol})
            if now - last_emit >= interval_seconds:
                await websocket.send_json({"type": "new", "candle": current_bar.copy(), "volume": current_vol.copy()})
                current_bar = {"time": int(now), "open": current_bar["close"],
                               "high": current_bar["close"], "low": current_bar["close"], "close": current_bar["close"]}
                current_vol = {"time": int(now), "value": 0.0}
                last_emit = now
    except WebSocketDisconnect:
        logger.info(f"Client disconnected from OHLCV stream for {ticker}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        try:
            await websocket.close()
        except RuntimeError:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
