import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AnalyzeResponse } from "@/lib/types";
import { ArrowUp, ArrowDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";

interface SignalCardProps {
  analysis: AnalyzeResponse;
}

export default function SignalCard({ analysis }: SignalCardProps) {
  const signalColor =
    analysis.signal === "BUY"
      ? "text-green-500"
      : analysis.signal === "SELL"
      ? "text-red-500"
      : "text-yellow-500";

  const SignalIcon =
    analysis.signal === "BUY"
      ? ArrowUp
      : analysis.signal === "SELL"
      ? ArrowDown
      : Minus;

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">{analysis.ticker}</CardTitle>
          <Badge
            variant={
              analysis.signal === "BUY"
                ? "default"
                : analysis.signal === "SELL"
                ? "destructive"
                : "secondary"
            }
          >
            <SignalIcon className="h-3 w-3 mr-1" />
            {analysis.signal}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-muted-foreground">Confidence</span>
          <span className={cn("font-bold", signalColor)}>
            {(analysis.confidence * 100).toFixed(1)}%
          </span>
        </div>
        <div className="w-full bg-muted rounded-full h-2">
          <div
            className={cn(
              "h-2 rounded-full transition-all",
              analysis.signal === "BUY"
                ? "bg-green-500"
                : analysis.signal === "SELL"
                ? "bg-red-500"
                : "bg-yellow-500"
            )}
            style={{ width: `${analysis.confidence * 100}%` }}
          />
        </div>
        <div className="space-y-1">
          {analysis.breakdown.slice(0, 4).map((ind) => (
            <div key={ind.name} className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">{ind.name}</span>
              <span
                className={cn(
                  "font-medium",
                  ind.signal === "BUY"
                    ? "text-green-500"
                    : ind.signal === "SELL"
                    ? "text-red-500"
                    : "text-yellow-500"
                )}
              >
                {ind.signal}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
