"""Trade-idea and paper-execution endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.core.data_loader import DataLoader
from app.core.trading_engine import build_trade_idea, paper_book
from app.schemas import PaperOrderRequest, PaperOrderResponse, PaperPortfolioResponse, TradeIdeaRequest, TradeIdeaResponse

router = APIRouter()


@router.post("/idea", response_model=TradeIdeaResponse)
async def create_trade_idea(request: TradeIdeaRequest):
    data = await DataLoader().load_async([request.ticker.upper()], interval=request.interval, period=request.period)
    frame = data.get(request.ticker.upper())
    if frame is None or len(frame) < 30:
        raise HTTPException(status_code=422, detail="At least 30 candles are required to build a trade idea")
    return build_trade_idea(frame, request)


@router.get("/paper-portfolio", response_model=PaperPortfolioResponse)
async def get_paper_portfolio():
    return paper_book.snapshot()


@router.post("/paper-orders", response_model=PaperOrderResponse, status_code=201)
async def create_paper_order(request: PaperOrderRequest):
    try:
        return paper_book.submit(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
