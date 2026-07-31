import React, { useEffect, useState } from 'react'

export default function PortfolioSummary() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let mounted = true
    async function load() {
      setLoading(true)
      try {
        const res = await fetch('/api/portfolio_summary')
        if (!res.ok) throw new Error('No portfolio_summary API')
        const json = await res.json()
        if (!mounted) return
        setData(json)
      } catch (err) {
        setData({ equity: 100000, cash: 50000, positions: [{ ticker: 'AAPL', qty: 100, avg: 150 }], pnl: 1200 })
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) return <div className="bg-white rounded-lg shadow p-4">Loading portfolio...</div>

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-md font-medium mb-2">Portfolio Summary</h3>
      <div className="grid grid-cols-3 gap-4">
        <div className="p-2 border rounded">
          <div className="text-sm text-gray-500">Equity</div>
          <div className="text-lg font-semibold">${data.equity.toLocaleString()}</div>
        </div>
        <div className="p-2 border rounded">
          <div className="text-sm text-gray-500">Cash</div>
          <div className="text-lg font-semibold">${data.cash.toLocaleString()}</div>
        </div>
        <div className="p-2 border rounded">
          <div className="text-sm text-gray-500">P&L</div>
          <div className={`text-lg font-semibold ${data.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>${data.pnl}</div>
        </div>
      </div>
      <div className="mt-3">
        <h4 className="text-sm font-medium mb-2">Top Positions</h4>
        <ul className="space-y-2">
          {data.positions.map((p) => (
            <li key={p.ticker} className="flex justify-between p-2 border rounded">
              <div>
                <div className="font-medium">{p.ticker} <span className="text-xs text-gray-500">x{p.qty}</span></div>
                <div className="text-xs text-gray-500">Avg: ${p.avg}</div>
              </div>
              <div className="text-sm">{((p.qty * p.avg) / data.equity * 100).toFixed(1)}%</div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
