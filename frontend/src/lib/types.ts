export interface Candle {
  time: number | string;
  open: number;
  high: number;
  low: number;
  close: number;
}

export interface Volume {
  time: number | string;
  value: number;
}

export interface OHLCVResponse {
  candles: Candle[];
  volumes: Volume[];
}

export interface MarketOverviewItem {
  ticker: string;
  price: number | null;
  change: number | null;
  change_percent: number | null;
}

export interface IndicatorBreakdown {
  name: string;
  signal: string;
  confidence: number;
  score: number;
  details: Record<string, number>;
}

export interface AnalyzeResponse {
  ticker: string;
  signal: string;
  confidence: number;
  score: number;
  breakdown: IndicatorBreakdown[];
}

export interface BacktestRequest {
  ticker: string;
  strategy: string;
  period: string;
  initial_cash: number;
}

export interface TradeRecord {
  entry_time: string;
  exit_time: string | null;
  side: string;
  entry_price: number;
  exit_price: number | null;
  pnl: number | null;
}

export interface BacktestResponse {
  summary: Record<string, number>;
  trades: TradeRecord[];
  equity: Record<string, number>[];
}

export interface PredictResponse {
  ticker: string;
  prediction: string;
  bullish_prob: number;
  bearish_prob: number;
  confidence: number;
}

export interface Portfolio {
  id: number;
  name: string;
  cash: number;
  created_at: string;
}

export interface Watchlist {
  id: number;
  name: string;
  symbols: string[];
  created_at: string;
}
