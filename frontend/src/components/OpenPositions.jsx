import React, { useEffect, useState } from 'react'

export default function OpenPositions() {
  const [positions, setPositions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let mounted = true
    async function load() {
      setLoading(true)
      try {
        const res = await fetch('/api/open_positions')
        if (!res.ok) throw new Error('No open_positions API')
        const json = await res.json()
        if (!mounted) return
        setPositions(json.positions || [])
      } catch (err) {
        setPositions([
          { ticker: 'AAPL', qty: 100, entry: 150, current: 152, pnl: 200 },
          { ticker: 'TSLA', qty: 10, entry: 700, current: 690, pnl: -100 },
        ])
      } finally {
        setLoading(false)
      }
    }
    load()
    const iv = setInterval(load, 5000)
    return () => clearInterval(iv)
  }, [])

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-md font-medium mb-2">Open Positions</h3>
      {loading && <div className="text-sm text-gray-500">Loading...</div>}
      <ul className="space-y-2 mt-2">
        {positions.map((p, i) => (
          <li key={i} className="flex justify-between items-center p-2 border rounded">
            <div>
              <div className="font-medium">{p.ticker} <span className="text-xs text-gray-500">x{p.qty}</span></div>
              <div className="text-xs text-gray-500">Entry: ${p.entry} • Current: ${p.current}</div>
            </div>
            <div className={`font-semibold ${p.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>${p.pnl}</div>
          </li>
        ))}
      </ul>
    </div>
  )
}
