import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import MarketOverview from "@/components/MarketOverview";
import SignalCard from "@/components/SignalCard";
import PortfolioSummary from "@/components/PortfolioSummary";
import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { AnalyzeResponse } from "@/lib/types";
import Mt5Panel from "@/components/Mt5Panel";

export default function Dashboard() {
  const [tickers] = useState(["AAPL", "MSFT", "GOOGL"]);
  const { data: analysis } = useQuery({
    queryKey: ["analysis", tickers],
    queryFn: async () => {
      const res = await api.post("/analysis/analyze", { tickers, interval: "1d", period: "1mo" });
      return res.data as AnalyzeResponse[];
    },
  });
  return (
    <div className="space-y-6">
      <div><p className="text-sm font-medium uppercase tracking-[0.2em] text-primary">Trading intelligence</p><h1 className="mt-2 text-3xl font-bold">Your market, in motion</h1><p className="mt-1 text-muted-foreground">Monitor live candles and connect your MetaTrader 5 terminal.</p></div>
      <PortfolioSummary cash={100000} totalValue={105420} totalReturn={5.42} />
      <Card>
        <CardHeader><CardTitle>Live market</CardTitle><p className="text-sm text-muted-foreground">Real MT5 data when the terminal bridge is available; otherwise a clearly marked demo stream.</p></CardHeader>
        <CardContent><Mt5Panel initialTicker="EURUSD" /></CardContent>
      </Card>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader><CardTitle>Market Sentiment</CardTitle></CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {analysis?.map((item) => <SignalCard key={item.ticker} analysis={item} />)}
              </div>
            </CardContent>
          </Card>
        </div>
        <div><MarketOverview /></div>
      </div>
    </div>
  );
}
