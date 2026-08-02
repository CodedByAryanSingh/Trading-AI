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
cp ../.env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

> Recommended Python version: 3.11 or 3.12 for compatibility with the backend data and ML dependencies.

### MetaTrader 5 connection

The live chart connects to MetaTrader 5 when the Python `MetaTrader5` package and a running terminal are available. Install that package on a supported MT5 host, then set these backend values in `.env`:

```bash
MT5_ENABLED=true
MT5_PATH=/path/to/terminal
MT5_LOGIN=12345678
MT5_PASSWORD=your-password
MT5_SERVER=your-broker-server
```

If the terminal is unavailable, the UI labels the connection as `Demo feed` and continues to provide a working live candlestick stream for development.

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
| POST /api/v1/trading/idea | Risk-gated BUY, SELL, or HOLD trade plan |
| GET /api/v1/trading/paper-portfolio | Paper trading risk and order ledger |
| POST /api/v1/trading/paper-orders | Create a paper-only order from a trade plan |
| GET /api/v1/market/export | Download historical data as CSV or Parquet |

## Trading workspace

Open `/trade` to use the live-chart workspace. It combines MT5 candle streaming, strategy consensus, entry/stop/target planning, and a paper-only order ticket. The decision engine requires multi-strategy alignment and at least 55% confidence before it makes a trade available; otherwise it returns `HOLD`.

The default market-data adapter uses Yahoo Finance symbols, which cover stocks, ETFs, many indices, futures, crypto pairs, and forex pairs. The architecture keeps provider access behind the market-data service so a broker or exchange feed can be added without changing strategies or the UI.

If the provider is offline, the workspace switches to clearly labelled demo data and forces `HOLD`; it never creates an executable paper recommendation from fallback data.

> Paper execution is intentionally the only execution mode in this project. Live broker orders need a separate, explicit account authorization and safety review.

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
