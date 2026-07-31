import React from 'react'

export default function BacktestResults(): JSX.Element {
  // placeholder data - integrate API to fetch real backtest results
  const sample = {
    start: '2024-01-01',
    end: '2024-06-30',
    trades: 12,
    netProfit: 12345.67,
    maxDrawdown: 0.12,
    sharpe: 1.45,
  }

  return (
    <div className="space-y-6">
      <section className="bg-white rounded-lg shadow p-4">
        <h2 className="text-lg font-medium mb-4">Backtest Summary</h2>
        <div className="grid grid-cols-4 gap-4">
          <div className="p-4 border rounded">Period: <strong>{sample.start} → {sample.end}</strong></div>
          <div className="p-4 border rounded">Trades: <strong>{sample.trades}</strong></div>
          <div className="p-4 border rounded">Net Profit: <strong>${sample.netProfit.toLocaleString()}</strong></div>
          <div className="p-4 border rounded">Max Drawdown: <strong>{(sample.maxDrawdown * 100).toFixed(2)}%</strong></div>
        </div>
      </section>

      <section className="bg-white rounded-lg shadow p-4">
        <h2 className="text-lg font-medium mb-4">Metrics</h2>
        <ul className="list-disc pl-6">
          <li>Sharpe Ratio: <strong>{sample.sharpe}</strong></li>
          <li>Win Rate: <strong>58%</strong></li>
          <li>Profit Factor: <strong>1.8</strong></li>
        </ul>
      </section>
    </div>
  )
}
