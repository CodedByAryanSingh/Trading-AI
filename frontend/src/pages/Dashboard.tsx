import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import MarketOverview from "@/components/MarketOverview";
import SignalCard from "@/components/SignalCard";
import PortfolioSummary from "@/components/PortfolioSummary";
import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { AnalyzeResponse } from "@/lib/types";

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
      <h1 className="text-3xl font-bold">Dashboard</h1>
      <PortfolioSummary cash={100000} totalValue={105420} totalReturn={5.42} />
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
