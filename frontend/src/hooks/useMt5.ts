import { useEffect, useState } from "react";
import { useWebSocket } from "./useWebSocket";
import { Candle, Volume } from "@/lib/types";

export function useMt5(ticker = "EURUSD", timeframe = "1m") {
  const wsBase = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws";
  const url = `${wsBase}/mt5?ticker=${encodeURIComponent(ticker)}&tf=${encodeURIComponent(timeframe)}`;
  const { data, connected, send } = useWebSocket(url);
  const [candles, setCandles] = useState<Candle[]>([]);
  const [volumes] = useState<Volume[]>([]);

  useEffect(() => {
    if (!data) return;
    if (data.type === "tick") {
      // append/update latest working candle
      const t = Math.floor(data.time / 60) * 60; // floor to minute
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
    } else if (data.type === "info") {
      // ignore for now
    }
  }, [data]);

  const setTicker = (t: string) => send(`set_ticker:${t}`);
  const setTimeframe = (tf: string) => send(`set_tf:${tf}`);

  return { candles, volumes, connected, setTicker, setTimeframe };
}
