import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import api from "@/lib/api";
import { BacktestResponse } from "@/lib/types";

interface BacktestFormProps {
  onResult: (result: BacktestResponse) => void;
}

const strategies = ["sma", "ema", "rsi", "macd", "bollinger", "trend", "breakout", "smc", "ict"];
const periods = ["1mo", "3mo", "6mo", "1y", "2y"];

export default function BacktestForm({ onResult }: BacktestFormProps) {
  const [ticker, setTicker] = useState("AAPL");
  const [strategy, setStrategy] = useState("sma");
  const [period, setPeriod] = useState("6mo");
  const [cash, setCash] = useState(100000);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.post("/backtest/run", {
        ticker,
        strategy,
        period,
        initial_cash: cash,
      });
      onResult(res.data);
    } catch (err) {
      console.error("Backtest failed:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Run Backtest</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Ticker</label>
              <Input value={ticker} onChange={(e) => setTicker(e.target.value.toUpperCase())} />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Initial Cash</label>
              <Input type="number" value={cash} onChange={(e) => setCash(Number(e.target.value))} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Strategy</label>
              <select
                value={strategy}
                onChange={(e) => setStrategy(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                {strategies.map((s) => (
                  <option key={s} value={s}>{s.toUpperCase()}</option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Period</label>
              <select
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                {periods.map((p) => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>
          </div>
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "Running..." : "Run Backtest"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
