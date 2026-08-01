import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import SignalCard from "@/components/SignalCard";
import api from "@/lib/api";
import { AnalyzeResponse } from "@/lib/types";
import Mt5Panel from "@/components/Mt5Panel";

export default function MarketAnalysis() {
  const [tickers, setTickers] = useState("AAPL,MSFT,GOOGL");
  const [submitted, setSubmitted] = useState(tickers);
  const { data, isLoading } = useQuery({
    queryKey: ["analysis", submitted],
    queryFn: async () => {
      const res = await api.post("/analysis/analyze", {
        tickers: submitted.split(",").map((t) => t.trim()), interval: "1d", period: "1y",
      });
      return res.data as AnalyzeResponse[];
    },
    enabled: !!submitted,
  });
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Market Analysis</h1>
      <div className="flex gap-2 max-w-lg">
        <Input value={tickers} onChange={(e) => setTickers(e.target.value)} placeholder="Comma-separated tickers" />
        <Button onClick={() => setSubmitted(tickers)}>Analyze</Button>
      </div>
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => <div key={i} className="h-64 bg-muted rounded animate-pulse" />)}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data?.map((item) => <SignalCard key={item.ticker} analysis={item} />)}
        </div>
      )}
      <div className="mt-8">
        <h2 className="text-2xl font-semibold">MT5 Live (Simulated)</h2>
        <p className="text-sm text-muted-foreground">Simulated MT5 stream — live candles from backend MT5 simulator.</p>
        <div className="mt-4">
          {/* Lazy load the Mt5Panel to avoid SSR issues */}
          <Mt5Panel initialTicker="EURUSD" />
        </div>
      </div>
    </div>
  );
}
