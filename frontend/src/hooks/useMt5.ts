import { useEffect, useState } from "react";
import { useWebSocket } from "./useWebSocket";
import { Candle, Volume } from "@/lib/types";

export function useMt5(ticker = "EURUSD", timeframe = "1m") {
  const wsBase = import.meta.env.VITE_WS_URL || (import.meta.env.DEV ? "ws://localhost:8000/ws" : `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}/ws`);
  const url = `${wsBase}/mt5?ticker=${encodeURIComponent(ticker)}&tf=${encodeURIComponent(timeframe)}`;
  const { data, connected } = useWebSocket(url);
  const [candles, setCandles] = useState<Candle[]>([]);
  const [volumes, setVolumes] = useState<Volume[]>([]);
  const [source, setSource] = useState<"mt5" | "simulator">("simulator");

  useEffect(() => {
    if (!data) return;
    if (data.type === "status") {
      setSource(data.source === "mt5" ? "mt5" : "simulator");
    } else if (data.type === "history") {
      setCandles(data.candles.map((c: Candle) => ({ ...c })));
      setVolumes(data.candles.map((c: Candle & { volume?: number }) => ({ time: c.time, value: c.volume ?? 0 })));
    } else if (data.type === "tick") {
      const timeframeSeconds: Record<string, number> = { "1m": 60, "5m": 300, "15m": 900, "1h": 3600, "4h": 14400, "1d": 86400 };
      const t = Math.floor(data.time / (timeframeSeconds[timeframe] ?? 60)) * (timeframeSeconds[timeframe] ?? 60);
      setCandles((prev) => {
        const last = prev[prev.length - 1];
        const price = data.price;
        if (!last || last.time !== t) {
          const newCandle: Candle = { time: t as any, open: price, high: price, low: price, close: price };
          return [...prev.slice(-200), newCandle];
        } else {
          const updated = { ...last, high: Math.max(last.high, price), low: Math.min(last.low, price), close: price };
          return [...prev.slice(0, -1), updated];
        }
      });
    } else if (data.type === "candle") {
      const c = { time: data.time as any, open: data.open, high: data.high, low: data.low, close: data.close };
      setCandles((prev) => [...prev.slice(-500), c]);
    }
  }, [data, timeframe]);

  return { candles, volumes, connected, source };
}
