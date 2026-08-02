import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, Bot, CheckCircle2, Loader2, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import api from "@/lib/api";
import { PaperPortfolio, TradeIdea } from "@/lib/types";

interface TradeIdeaPanelProps {
  ticker: string;
  timeframe: string;
}

const formatPrice = (value: number | null) => value === null ? "—" : value.toFixed(value < 10 ? 5 : 2);

export default function TradeIdeaPanel({ ticker, timeframe }: TradeIdeaPanelProps) {
  const client = useQueryClient();
  const ideaQuery = useQuery({
    queryKey: ["trade-idea", ticker, timeframe],
    queryFn: async () => (await api.post("/trading/idea", { ticker, interval: timeframe, period: "6mo", risk_percent: 0.01 })).data as TradeIdea,
    enabled: Boolean(ticker),
  });
  const portfolioQuery = useQuery({
    queryKey: ["paper-portfolio"],
    queryFn: async () => (await api.get("/trading/paper-portfolio")).data as PaperPortfolio,
  });
  const orderMutation = useMutation({
    mutationFn: async (idea: TradeIdea) => api.post("/trading/paper-orders", {
      ticker: idea.ticker, side: idea.action, entry_price: idea.entry_price,
      stop_loss: idea.stop_loss, take_profit: idea.take_profit, risk_percent: 0.01,
    }),
    onSuccess: () => client.invalidateQueries({ queryKey: ["paper-portfolio"] }),
  });
  const idea = ideaQuery.data;
  const canPaperTrade = idea?.status === "ready" && idea.action !== "HOLD" && idea.stop_loss && idea.take_profit;

  return (
    <div className="space-y-4">
      <Card className="border-primary/20 bg-gradient-to-br from-card to-primary/5">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between"><CardTitle className="flex items-center gap-2 text-base"><Bot className="h-4 w-4 text-primary" /> AI trade idea</CardTitle><span className="rounded-full bg-amber-500/15 px-2.5 py-1 text-xs font-semibold text-amber-600 dark:text-amber-400">PAPER ONLY</span></div>
        </CardHeader>
        <CardContent>
          {ideaQuery.isLoading && <div className="flex h-44 items-center justify-center text-sm text-muted-foreground"><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Evaluating alignment…</div>}
          {ideaQuery.isError && <div className="flex min-h-44 items-center gap-2 text-sm text-destructive"><AlertTriangle className="h-4 w-4" /> Market data is unavailable for this symbol.</div>}
          {idea && <div className="space-y-4">
            <div className="flex items-end justify-between"><div><p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Decision</p><p className={idea.action === "BUY" ? "mt-1 text-3xl font-bold text-emerald-500" : idea.action === "SELL" ? "mt-1 text-3xl font-bold text-rose-500" : "mt-1 text-3xl font-bold text-amber-500"}>{idea.action}</p></div><div className="text-right"><p className="text-xs text-muted-foreground">Confidence</p><p className="mt-1 text-xl font-semibold">{(idea.confidence * 100).toFixed(0)}%</p><p className={idea.data_source === "provider" ? "mt-1 text-xs text-emerald-500" : "mt-1 text-xs text-amber-500"}>{idea.data_source === "provider" ? "Provider data" : "Demo data"}</p></div></div>
            <div className="grid grid-cols-2 gap-x-4 gap-y-3 border-y py-4 text-sm"><Metric label="Entry" value={formatPrice(idea.entry_price)} /><Metric label="Stop loss" value={formatPrice(idea.stop_loss)} /><Metric label="Take profit" value={formatPrice(idea.take_profit)} /><Metric label="Reward / risk" value={idea.risk_reward ? `${idea.risk_reward.toFixed(1)}R` : "—"} /></div>
            <div className="space-y-2">{idea.reasons.slice(0, 3).map((reason) => <p key={reason} className="flex gap-2 text-xs text-muted-foreground"><CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary" />{reason}</p>)}</div>
            <Button className="w-full" disabled={!canPaperTrade || orderMutation.isPending} onClick={() => idea && orderMutation.mutate(idea)}>{orderMutation.isPending ? "Opening paper position…" : canPaperTrade ? `Open ${idea.action} paper trade` : "Waiting for a qualified setup"}</Button>
            {orderMutation.isError && <p className="text-xs text-destructive">Unable to open the paper order. Check the trade plan.</p>}
          </div>}
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="pb-3"><CardTitle className="flex items-center gap-2 text-base"><ShieldCheck className="h-4 w-4 text-primary" /> Risk controls</CardTitle></CardHeader>
        <CardContent className="space-y-3 text-sm"><div className="flex justify-between"><span className="text-muted-foreground">Paper capital</span><span>${portfolioQuery.data?.starting_cash.toLocaleString() ?? "100,000"}</span></div><div className="flex justify-between"><span className="text-muted-foreground">Open risk</span><span>${portfolioQuery.data?.reserved_risk.toLocaleString() ?? "0"}</span></div><div className="flex justify-between"><span className="text-muted-foreground">Max risk / trade</span><span>1.0%</span></div><p className="border-t pt-3 text-xs text-muted-foreground">Stops new paper trades only when the AI and risk rules align. Real broker orders are disabled.</p></CardContent>
      </Card>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div><p className="text-xs text-muted-foreground">{label}</p><p className="mt-1 font-medium">{value}</p></div>;
}
