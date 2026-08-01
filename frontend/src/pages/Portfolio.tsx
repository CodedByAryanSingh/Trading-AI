import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import PortfolioSummary from "@/components/PortfolioSummary";
import api from "@/lib/api";
import { Portfolio as PortfolioType, Watchlist } from "@/lib/types";

export default function Portfolio() {
  const { data: portfolios } = useQuery({
    queryKey: ["portfolios"],
    queryFn: async () => { const res = await api.get("/portfolio/portfolios"); return res.data as PortfolioType[]; },
  });
  const { data: watchlists } = useQuery({
    queryKey: ["watchlists"],
    queryFn: async () => { const res = await api.get("/portfolio/watchlists"); return res.data as Watchlist[]; },
  });
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Portfolio</h1>
      <PortfolioSummary cash={portfolios?.[0]?.cash || 100000} totalValue={portfolios?.[0]?.cash || 100000} totalReturn={0} />
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader><CardTitle>Portfolios</CardTitle></CardHeader>
          <CardContent>
            {portfolios?.map((p) => (
              <div key={p.id} className="flex justify-between py-2 border-b last:border-0">
                <span>{p.name}</span><span className="font-medium">${p.cash.toLocaleString()}</span>
              </div>
            )) || <p className="text-muted-foreground">No portfolios found.</p>}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Watchlists</CardTitle></CardHeader>
          <CardContent>
            {watchlists?.map((w) => (
              <div key={w.id} className="py-2 border-b last:border-0">
                <div className="font-medium mb-1">{w.name}</div>
                <div className="flex flex-wrap gap-2">
                  {w.symbols.map((s) => <span key={s} className="px-2 py-1 bg-muted rounded text-xs font-medium">{s}</span>)}
                </div>
              </div>
            )) || <p className="text-muted-foreground">No watchlists found.</p>}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
