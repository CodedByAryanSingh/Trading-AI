import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import api from "@/lib/api";
import { PredictResponse } from "@/lib/types";

export default function AIPredictions() {
  const [ticker, setTicker] = useState("AAPL");
  const [submitted, setSubmitted] = useState("AAPL");
  const { data, isLoading } = useQuery({
    queryKey: ["prediction", submitted],
    queryFn: async () => {
      const res = await api.post("/predictions/predict", { ticker: submitted, horizon: "1d" });
      return res.data as PredictResponse;
    },
    enabled: !!submitted,
  });
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">AI Predictions</h1>
      <div className="flex gap-2 max-w-md">
        <Input value={ticker} onChange={(e) => setTicker(e.target.value.toUpperCase())} placeholder="Enter ticker" />
        <Button onClick={() => setSubmitted(ticker)}>Predict</Button>
      </div>
      {isLoading && <div className="h-48 bg-muted rounded animate-pulse max-w-md" />}
      {data && (
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>{data.ticker}</span>
              <Badge variant={data.prediction === "bullish" ? "default" : data.prediction === "bearish" ? "destructive" : "secondary"}>
                {data.prediction.toUpperCase()}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {[["Bullish Probability", data.bullish_prob, "green"], ["Bearish Probability", data.bearish_prob, "red"]].map(([label, val, color]) => (
              <div key={String(label)} className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">{String(label)}</span>
                  <span className={`font-medium text-${color}-500`}>{((val as number) * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-muted rounded-full h-2">
                  <div className={`h-2 rounded-full bg-${color}-500`} style={{ width: `${(val as number) * 100}%` }} />
                </div>
              </div>
            ))}
            <div className="pt-2 border-t flex justify-between">
              <span className="text-muted-foreground">Confidence</span>
              <span className="font-bold">{(data.confidence * 100).toFixed(1)}%</span>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
