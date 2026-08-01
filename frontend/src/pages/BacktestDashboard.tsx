import { useNavigate } from "react-router-dom";
import BacktestForm from "@/components/BacktestForm";
import { BacktestResponse } from "@/lib/types";

export default function BacktestDashboard() {
  const navigate = useNavigate();
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Backtest Dashboard</h1>
      <div className="max-w-2xl">
        <BacktestForm onResult={(result: BacktestResponse) => navigate("/backtest/results", { state: { result } })} />
      </div>
    </div>
  );
}
