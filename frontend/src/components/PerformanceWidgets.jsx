import React, { useEffect, useState } from 'react'

export default function PerformanceWidgets() {
  const [metrics, setMetrics] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let mounted = true
    async function load() {
      setLoading(true)
      try {
        const res = await fetch('/api/performance')
        if (!res.ok) throw new Error('No performance API')
        const json = await res.json()
        if (!mounted) return
        setMetrics(json)
      } catch (err) {
        setMetrics({ equity: 100000, pnl: 1200, winRate: 0.56, sharpe: 1.2 })
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) return <div className="bg-white rounded-lg shadow p-4">Loading performance...</div>

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-md font-medium mb-2">Performance</h3>
      <div className="grid grid-cols-4 gap-4">
        <div className="p-3 border rounded">
          <div className="text-sm text-gray-500">Equity</div>
          <div className="text-lg font-semibold">${metrics.equity.toLocaleString()}</div>
        </div>
        <div className="p-3 border rounded">
          <div className="text-sm text-gray-500">PnL</div>
          <div className={`text-lg font-semibold ${metrics.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>${metrics.pnl}</div>
        </div>
        <div className="p-3 border rounded">
          <div className="text-sm text-gray-500">Win Rate</div>
          <div className="text-lg font-semibold">{(metrics.winRate * 100).toFixed(1)}%</div>
        </div>
        <div className="p-3 border rounded">
          <div className="text-sm text-gray-500">Sharpe</div>
          <div className="text-lg font-semibold">{metrics.sharpe}</div>
        </div>
      </div>
    </div>
  )
}
