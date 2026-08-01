import { Routes, Route } from "react-router-dom";
import Layout from "@/components/Layout";
import Dashboard from "@/pages/Dashboard";
import Auth from "@/pages/Auth";
import MarketExplorer from "@/pages/MarketExplorer";
import MarketAnalysis from "@/pages/MarketAnalysis";
import AIPredictions from "@/pages/AIPredictions";
import BacktestDashboard from "@/pages/BacktestDashboard";
import BacktestResults from "@/pages/BacktestResults";
import Portfolio from "@/pages/Portfolio";
import StrategyResults from "@/pages/StrategyResults";

export default function App() {
  return (
    <Routes>
      <Route path="/auth" element={<Auth />} />
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/market" element={<MarketExplorer />} />
        <Route path="/analysis" element={<MarketAnalysis />} />
        <Route path="/predictions" element={<AIPredictions />} />
        <Route path="/backtest" element={<BacktestDashboard />} />
        <Route path="/backtest/results" element={<BacktestResults />} />
        <Route path="/portfolio" element={<Portfolio />} />
        <Route path="/strategy-results" element={<StrategyResults />} />
      </Route>
    </Routes>
  );
}
