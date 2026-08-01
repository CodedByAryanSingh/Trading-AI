import { useState } from "react";
import Chart from "@/components/Chart";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useMt5 } from "@/hooks/useMt5";

export default function Mt5Panel({ initialTicker = "EURUSD" }: { initialTicker?: string }) {
  const [ticker, setTicker] = useState(initialTicker);
  const [tf, setTf] = useState("1m");
  const { candles, connected, setTicker: setTickerRemote, setTimeframe } = useMt5(ticker, tf);

  return (
    <div className="space-y-4">
      <div className="flex gap-2 items-center">
        <Input value={ticker} onChange={(e) => setTicker(e.target.value)} />
        <Input value={tf} onChange={(e) => setTf(e.target.value)} />
        <Button onClick={() => { setTickerRemote(ticker); setTimeframe(tf); }}>
          Subscribe
        </Button>
        <div className="ml-auto text-sm">Status: {connected ? <span className="text-green-500">Connected</span> : <span className="text-red-500">Disconnected</span>}</div>
      </div>
      <div className="bg-card p-2 rounded">
        <Chart candles={candles} volumes={[]} height={400} />
      </div>
    </div>
  );
}
