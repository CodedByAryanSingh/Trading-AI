import { useQuery } from "@tanstack/react-query";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MarketOverviewItem } from "@/lib/types";
import { formatCurrency, formatPercent } from "@/lib/utils";
import api from "@/lib/api";

export default function MarketOverview() {
  const { data, isLoading } = useQuery({
    queryKey: ["market-overview"],
    queryFn: async () => {
      const res = await api.get("/market/overview?tickers=AAPL,MSFT,GOOGL,AMZN,TSLA");
      return res.data.data as MarketOverviewItem[];
    },
    refetchInterval: 30000,
  });

  if (isLoading) {
    return (
      <Card>
        <CardHeader><CardTitle>Market Overview</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-2">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-12 bg-muted rounded animate-pulse" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Market Overview</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {data?.map((item) => (
          <div key={item.ticker} className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="font-semibold w-16">{item.ticker}</span>
              <span className="text-muted-foreground">
                {item.price ? formatCurrency(item.price) : "—"}
              </span>
            </div>
            <div className="flex items-center gap-2">
              {item.change_percent !== null ? (
                <Badge
                  variant={item.change_percent >= 0 ? "default" : "destructive"}
                  className="flex items-center gap-1"
                >
                  {item.change_percent >= 0 ? (
                    <TrendingUp className="h-3 w-3" />
                  ) : (
                    <TrendingDown className="h-3 w-3" />
                  )}
                  {formatPercent(item.change_percent)}
                </Badge>
              ) : (
                <Badge variant="outline"><Minus className="h-3 w-3" /></Badge>
              )}
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
