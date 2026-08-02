import { useMemo, useState } from "react";
import { Activity, Circle } from "lucide-react";
import Chart from "@/components/Chart";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useMt5 } from "@/hooks/useMt5";

export default function Mt5Panel({ initialTicker = "EURUSD", initialTimeframe = "1m" }: { initialTicker?: string; initialTimeframe?: string }) {
  const [ticker, setTicker] = useState(initialTicker);
  const [tf, setTf] = useState(initialTimeframe);
  const [subscription, setSubscription] = useState({ ticker: initialTicker, tf: initialTimeframe });
  const { candles, connected, source } = useMt5(subscription.ticker, subscription.tf);
  const latest = candles[candles.length - 1];
  const price = latest?.close ?? 0;
  const change = latest ? latest.close - latest.open : 0;
  const precision = useMemo(() => subscription.ticker.includes("JPY") ? 3 : 5, [subscription.ticker]);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2 items-center">
        <Input className="w-32" value={ticker} onChange={(e) => setTicker(e.target.value.toUpperCase())} placeholder="Symbol" />
        <select className="h-10 rounded-md border bg-background px-3 text-sm" value={tf} onChange={(e) => setTf(e.target.value)}>
          {['1m', '5m', '15m', '1h', '4h', '1d'].map((value) => <option key={value}>{value}</option>)}
        </select>
        <Button onClick={() => setSubscription({ ticker: ticker || initialTicker, tf })}>
          <Activity className="mr-2 h-4 w-4" /> Connect
        </Button>
        <div className="ml-auto flex items-center gap-2 text-sm text-muted-foreground">
          <Circle className={connected ? "h-2.5 w-2.5 fill-emerald-500 text-emerald-500" : "h-2.5 w-2.5 fill-rose-500 text-rose-500"} />
          {connected ? (source === "mt5" ? "MT5 connected" : "Demo feed") : "Connecting"}
        </div>
      </div>
      <div className="flex items-end justify-between rounded-lg border bg-background/60 px-4 py-3">
        <div><p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">{subscription.ticker} · {subscription.tf}</p><p className="mt-1 text-2xl font-semibold">{price ? price.toFixed(precision) : "—"}</p></div>
        <p className={change >= 0 ? "text-emerald-500" : "text-rose-500"}>{change >= 0 ? "+" : ""}{change.toFixed(precision)}</p>
      </div>
      <div className="bg-card p-2 rounded">
        {candles.length ? <Chart candles={candles} volumes={[]} height={420} /> : <div className="flex h-[420px] items-center justify-center text-sm text-muted-foreground">Waiting for candle history…</div>}
      </div>
    </div>
  );
}
