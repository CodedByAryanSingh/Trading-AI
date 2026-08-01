import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import Chart from "@/components/Chart";
import { useOHLCV } from "@/hooks/useMarketData";

export default function MarketExplorer() {
  const [ticker, setTicker] = useState("AAPL");
  const [search, setSearch] = useState("AAPL");
  const { data, isLoading } = useOHLCV(ticker);
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Market Explorer</h1>
      <div className="flex gap-2 max-w-md">
        <Input placeholder="Enter ticker" value={search} onChange={(e) => setSearch(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && setTicker(search.toUpperCase())} />
        <Button onClick={() => setTicker(search.toUpperCase())}>Search</Button>
      </div>
      <Card>
        <CardHeader><CardTitle>{ticker} Chart</CardTitle></CardHeader>
        <CardContent>
          {isLoading ? <div className="h-[500px] bg-muted rounded animate-pulse" /> :
           data ? <Chart candles={data.candles} volumes={data.volumes} /> :
           <div className="h-[500px] flex items-center justify-center text-muted-foreground">No data available</div>}
        </CardContent>
      </Card>
    </div>
  );
}
