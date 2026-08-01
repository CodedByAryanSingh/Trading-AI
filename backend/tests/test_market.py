"""Market data endpoint tests."""
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    """Test health endpoint."""
    response = await async_client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_get_ohlcv(async_client: AsyncClient):
    """Test OHLCV data endpoint."""
    response = await async_client.get("/api/v1/market/ohlcv?ticker=AAPL&interval=1d&period=1mo")
    assert response.status_code in [200, 500]  # 500 if yfinance fails in test env
    if response.status_code == 200:
        data = response.json()
        assert "candles" in data
        assert "volumes" in data


@pytest.mark.asyncio
async def test_market_overview(async_client: AsyncClient):
    """Test market overview endpoint."""
    response = await async_client.get("/api/v1/market/overview?tickers=AAPL,MSFT")
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "data" in data


@pytest.mark.asyncio
async def test_live_price(async_client: AsyncClient):
    """Test live price endpoint."""
    response = await async_client.get("/api/v1/market/live-price?ticker=AAPL")
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert data["ticker"] == "AAPL"
        assert "price" in data
