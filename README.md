# Trading-AI

AI-Powered Quantitative Trading Intelligence Platform.

## Architecture

- **Backend**: FastAPI + SQLAlchemy (async) + PostgreSQL/SQLite
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS + shadcn/ui
- **ML**: scikit-learn ensemble models for price direction prediction
- **Data**: yfinance for market data with parquet caching

## Quick Start

### Docker (Recommended)
```bash
cp .env.example .env
docker-compose up --build
```

### Manual Setup
#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

> Recommended Python version: 3.11 or 3.12 for compatibility with the backend data and ML dependencies.

#### Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## API Endpoints

| Endpoint | Description |
|---|---|
| POST /api/v1/auth/register | User registration |
| POST /api/v1/auth/login | User login |
| GET /api/v1/market/ohlcv | OHLCV candlestick data |
| GET /api/v1/market/overview | Market overview |
| POST /api/v1/analysis/analyze | Multi-strategy analysis |
| POST /api/v1/backtest/run | Run backtest |
| POST /api/v1/predictions/predict | AI prediction |
| GET /api/v1/portfolio/portfolios | User portfolios |
| WS /ws/ohlcv | Real-time mock OHLCV stream |

## Strategies Included
- SMA/EMA Crossover
- RSI Overbought/Oversold
- MACD Histogram
- Bollinger Bands Mean Reversion
- Trend Following (Momentum)
- Support/Resistance Breakout
- Smart Money Concepts (SMC)
- Inner Circle Trader (ICT)

## Testing
```bash
cd backend
pytest -v
```

## License
MIT
