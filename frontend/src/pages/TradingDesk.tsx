import { useState } from "react";
import { Activity, Layers3, ShieldAlert } from "lucide-react";
import Mt5Panel from "@/components/Mt5Panel";
import TradeIdeaPanel from "@/components/TradeIdeaPanel";

export default function TradingDesk() {
  const [ticker, setTicker] = useState("EURUSD");
  const [timeframe, setTimeframe] = useState("1h");

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-end"><div><p className="text-sm font-medium uppercase tracking-[0.2em] text-primary">Execution workspace</p><h1 className="mt-2 text-3xl font-bold tracking-tight">Trade with a plan</h1><p className="mt-1 max-w-2xl text-muted-foreground">Live market context, ensemble signals, and strict paper-risk controls in one workspace.</p></div><div className="flex items-center gap-2 rounded-full border bg-card px-3 py-2 text-xs text-muted-foreground"><ShieldAlert className="h-3.5 w-3.5 text-amber-500" /> Live execution disabled</div></div>
      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
        <section className="space-y-4 rounded-xl border bg-card p-4 shadow-sm"><div className="flex flex-wrap items-center justify-between gap-3"><div className="flex items-center gap-2"><Layers3 className="h-4 w-4 text-primary" /><h2 className="font-semibold">Live candles</h2></div><div className="flex gap-2"><input aria-label="Symbol" className="h-9 w-28 rounded-md border bg-background px-3 text-sm uppercase" value={ticker} onChange={(event) => setTicker(event.target.value.toUpperCase())} /><select aria-label="Timeframe" className="h-9 rounded-md border bg-background px-2 text-sm" value={timeframe} onChange={(event) => setTimeframe(event.target.value)}>{["1m", "5m", "15m", "1h", "4h", "1d"].map((item) => <option key={item}>{item}</option>)}</select></div></div><Mt5Panel key={`${ticker}-${timeframe}`} initialTicker={ticker} initialTimeframe={timeframe} /></section>
        <aside><TradeIdeaPanel ticker={ticker} timeframe={timeframe} /></aside>
      </div>
      <div className="grid gap-4 md:grid-cols-3"><Insight icon={Activity} title="Continuous scan" copy="The decision engine weights trend, momentum, volatility, breakout, SMC, and ICT signals." /><Insight icon={ShieldAlert} title="Capital first" copy="Every paper idea sizes from stop distance and never risks more than the configured limit." /><Insight icon={Layers3} title="Multi-asset ready" copy="Use provider symbols for stocks, forex, crypto, ETFs, indices, and futures." /></div>
    </div>
  );
}

function Insight({ icon: Icon, title, copy }: { icon: typeof Activity; title: string; copy: string }) {
  return <div className="rounded-xl border bg-card p-5"><Icon className="h-5 w-5 text-primary" /><h3 className="mt-4 font-semibold">{title}</h3><p className="mt-1 text-sm leading-6 text-muted-foreground">{copy}</p></div>;
}
