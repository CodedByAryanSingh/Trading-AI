import { useLocation } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { BacktestResponse } from "@/lib/types";
import { formatCurrency } from "@/lib/utils";

export default function BacktestResults() {
  const location = useLocation();
  const result = location.state?.result as BacktestResponse | undefined;
  if (!result) return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Backtest Results</h1>
      <p className="text-muted-foreground">No backtest results available. Run a backtest first.</p>
    </div>
  );
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Backtest Results</h1>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Object.entries(result.summary).map(([key, value]) => (
          <Card key={key}>
            <CardHeader className="pb-2">
              <CardTitle className="text-xs font-medium uppercase text-muted-foreground">{key.replace(/_/g, " ")}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {typeof value === "number" && key.includes("cash") ? formatCurrency(value) : typeof value === "number" ? value.toFixed(2) : value}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      <Card>
        <CardHeader><CardTitle>Trades ({result.trades.length})</CardTitle></CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b">
                <th className="text-left py-2">Side</th>
                <th className="text-left py-2">Entry</th>
                <th className="text-left py-2">Exit</th>
                <th className="text-right py-2">P&L</th>
              </tr></thead>
              <tbody>
                {result.trades.slice(0, 20).map((trade, i) => (
                  <tr key={i} className="border-b last:border-0">
                    <td className="py-2"><Badge variant={trade.side === "LONG" ? "default" : "destructive"}>{trade.side}</Badge></td>
                    <td className="py-2">{trade.entry_price.toFixed(2)}</td>
                    <td className="py-2">{trade.exit_price ? trade.exit_price.toFixed(2) : "—"}</td>
                    <td className={`py-2 text-right ${(trade.pnl || 0) >= 0 ? "text-green-500" : "text-red-500"}`}>
                      {trade.pnl !== null ? trade.pnl!.toFixed(2) : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
