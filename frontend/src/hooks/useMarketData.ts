import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { OHLCVResponse, MarketOverviewItem } from "@/lib/types";

export function useOHLCV(ticker: string, interval = "1d", period = "1y") {
  return useQuery<OHLCVResponse>({
    queryKey: ["ohlcv", ticker, interval, period],
    queryFn: async () => {
      const res = await api.get(`/market/ohlcv?ticker=${ticker}&interval=${interval}&period=${period}`);
      return res.data;
    },
    enabled: !!ticker,
  });
}

export function useMarketOverview(tickers = "AAPL,MSFT,GOOGL") {
  return useQuery<MarketOverviewItem[]>({
    queryKey: ["market-overview", tickers],
    queryFn: async () => {
      const res = await api.get(`/market/overview?tickers=${tickers}`);
      return res.data.data;
    },
    refetchInterval: 30000,
  });
}
