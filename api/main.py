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


@app.get("/healthz")
async def healthz() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    logger.info("Starting Trading-AI API")
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)
