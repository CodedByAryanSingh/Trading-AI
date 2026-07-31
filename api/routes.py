"""
API routes for Trading-AI.

Defines a small set of endpoints for analysis and prediction that call into
the core DataLoader and StrategyEngine.
"""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException

from api.schemas import AnalyzeRequest, AnalyzeResponse
from data.data_loader import DataLoader
from strategies.strategy import StrategyEngine
from utils.logger import get_logger
from fastapi import HTTPException

logger = get_logger(__name__)

router = APIRouter()


@router.post("/analyze", response_model=List[AnalyzeResponse])
async def analyze(req: AnalyzeRequest):
    """Analyze tickers and return signals using the strategy engine."""
    dl = DataLoader()
    try:
        data_map = dl.load(req.tickers, interval=req.interval or "1d", period=req.period or "1y")
    except Exception as exc:
        logger.exception("Failed to load data: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to load market data")

    results = []
    for ticker, df in data_map.items():
        try:
            engine = StrategyEngine(df)
            out = engine.multi_indicator_confirmation(req.params or {})
            results.append(AnalyzeResponse(ticker=ticker, signal=out["signal"], confidence=out["confidence"], score=out["score"], breakdown=out.get("breakdown")))
        except Exception:
            logger.exception("Failed to analyze %s", ticker)
            # skip ticker on error
            continue

    return results


@router.get('/ohlcv')
async def get_ohlcv(ticker: str, interval: str = '1d', period: str = '1mo', start: str | None = None, end: str | None = None):
    """Return OHLCV data for a single ticker formatted for the frontend chart.

    Query parameters:
    - ticker: ticker symbol (required)
    - interval: data granularity (1d, 1h, 1m, etc.)
    - period: period alias (e.g., 1mo, 3mo, 1y) used when start/end omitted
    - start, end: ISO dates to define an explicit range (optional)
    """
    dl = DataLoader()
    try:
        data_map = dl.load([ticker], interval=interval, period=period)
        df = data_map.get(ticker)
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"No data for {ticker}")

        # Format data for lightweight-charts: time must be YYYY-MM-DD or unix timestamp
        candles = []
        volumes = []
        # decide whether to return unix timestamps (seconds) for intraday intervals
        use_unix = False
        if any(x in interval for x in ['m', 'h']):
            use_unix = True

        for idx, row in df.iterrows():
            # idx may be tz-aware Timestamp
            t = idx.to_pydatetime()
            if use_unix:
                # lightweight-charts expects unix seconds for numeric times
                time_val = int(t.timestamp())
            else:
                time_val = t.strftime('%Y-%m-%d')

            candles.append({
                'time': time_val,
                'open': float(row.get('Open', 0.0)),
                'high': float(row.get('High', 0.0)),
                'low': float(row.get('Low', 0.0)),
                'close': float(row.get('Close', 0.0)),
            })
            volumes.append({
                'time': time_val,
                'value': float(row.get('Volume', 0.0)),
            })

        return {'candles': candles, 'volumes': volumes}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception('Failed to fetch OHLCV for %s: %s', ticker, exc)
        raise HTTPException(status_code=500, detail='Failed to fetch OHLCV data')


# Additional lightweight endpoints used by the frontend
@router.get('/market_overview')
async def market_overview(tickers: str = 'AAPL'):
    """Return a simple market overview for the provided comma-separated tickers."""
    md = DataLoader()
    symbols = [t.strip() for t in tickers.split(',') if t.strip()]
    out = []
    for s in symbols:
        try:
            price = md._md.get_live_price(s)
            out.append({'ticker': s, 'price': float(price), 'change': 0.0})
        except Exception:
            out.append({'ticker': s, 'price': None, 'change': None})
    return {'data': out}


@router.get('/live_price')
async def live_price(ticker: str):
    """Return latest live price for a ticker."""
    md = DataLoader()
    try:
        price = md._md.get_live_price(ticker)
        return {'ticker': ticker, 'price': float(price)}
    except Exception as exc:
        logger.exception('Failed live_price for %s: %s', ticker, exc)
        raise HTTPException(status_code=500, detail='Failed to fetch live price')


@router.post('/signals')
async def signals(tickers: List[str], interval: str = '1d', period: str = '1mo'):
    """Return aggregated signals for a list of tickers using StrategyEngine."""
    dl = DataLoader()
    try:
        data_map = dl.load(tickers, interval=interval, period=period)
    except Exception as exc:
        logger.exception('Failed to load data for signals: %s', exc)
        raise HTTPException(status_code=500, detail='Failed to load market data')
    results = {}
    for t, df in data_map.items():
        try:
            engine = StrategyEngine(df)
            out = engine.multi_indicator_confirmation({})
            results[t] = out
        except Exception:
            logger.exception('Signal generation failed for %s', t)
            results[t] = {'error': 'failed'}
    return results


@router.post('/predict')
async def predict(ticker: str, interval: str = '1d'):
    """Return a simple placeholder prediction for a ticker.

    This uses models/predictor.Predictor if a model exists; otherwise returns a mock.
    """
    try:
        from models.predictor import Predictor
        from pandas import DataFrame

        # naive approach: load last few features from DataLoader and produce mock
        dl = DataLoader()
        data_map = dl.load([ticker], interval=interval, period='1mo')
        df = data_map.get(ticker)
        if df is None or df.empty:
            raise Exception('no data')
        # build a tiny feature row: last close and 3-day returns
        last = df.iloc[-10:]
        features = {
            'close': float(last['Close'].iloc[-1]) if 'Close' in last else float(last.iloc[-1][0]),
        }
        # no model on disk: return mock probabilities
        return {
            'ticker': ticker,
            'prediction': 'neutral',
            'bullish_prob': 0.5,
            'bearish_prob': 0.5,
            'confidence': 0.5,
        }
    except Exception as exc:
        logger.exception('Predict failed: %s', exc)
        raise HTTPException(status_code=500, detail='Prediction failed')


@router.post('/backtest')
async def run_backtest(ticker: str, strategy: str = 'sma', period: str = '6mo'):
    """Run a backtest for the given ticker and strategy using the backtest engine."""
    try:
        from backtest.engine import BacktestEngine
        import pandas as pd

        dl = DataLoader()
        data_map = dl.load([ticker], interval='1d', period=period)
        df = data_map.get(ticker)
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail='No data')
        # simple mock: assume strategy has produced a 'signal' column
        # For now, create a naive signal based on SMA crossover
        df = df.copy()
        df['signal'] = 0
        if strategy == 'sma':
            df['sma_short'] = df['Close'].rolling(10).mean()
            df['sma_long'] = df['Close'].rolling(30).mean()
            df.loc[df['sma_short'] > df['sma_long'], 'signal'] = 1
            df.loc[df['sma_short'] < df['sma_long'], 'signal'] = -1
        engine = BacktestEngine(initial_cash=100000)
        engine.run(df, signal_column='signal')
        trades = engine.trades
        equity = engine.equity_dataframe().reset_index().to_dict(orient='records')
        return {'summary': engine.summary(), 'trades': trades, 'equity': equity}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception('Backtest failed: %s', exc)
        raise HTTPException(status_code=500, detail='Backtest failed')
