import React, { useEffect, useState } from 'react'

export default function RecentSignals() {
  const [signals, setSignals] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let mounted = true
    async function load() {
      setLoading(true)
      try {
        const res = await fetch('/api/recent_signals')
        if (!res.ok) throw new Error('No recent_signals API')
        const json = await res.json()
        if (!mounted) return
        setSignals(json.signals || [])
      } catch (err) {
        setSignals([
          { time: '2026-07-31 10:12', ticker: 'AAPL', strategy: 'SMA', signal: 'BUY', confidence: 0.7 },
          { time: '2026-07-31 09:55', ticker: 'MSFT', strategy: 'RSI', signal: 'SELL', confidence: 0.6 },
        ])
      } finally {
        setLoading(false)
      }
    }
    load()
    const iv = setInterval(load, 15000)
    return () => clearInterval(iv)
  }, [])

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-md font-medium mb-2">Recent Signals</h3>
      {loading && <div className="text-sm text-gray-500">Loading...</div>}
      <ul className="space-y-2 mt-2">
        {signals.map((s, i) => (
          <li key={i} className="flex justify-between items-center p-2 border rounded">
            <div>
              <div className="font-medium">{s.ticker} — {s.strategy}</div>
              <div className="text-xs text-gray-500">{s.time}</div>
            </div>
            <div className={`font-semibold ${s.signal === 'BUY' ? 'text-green-600' : s.signal === 'SELL' ? 'text-red-600' : 'text-gray-600'}`}>{s.signal} {(s.confidence*100).toFixed(0)}%</div>
          </li>
        ))}
      </ul>
    </div>
  )
}
