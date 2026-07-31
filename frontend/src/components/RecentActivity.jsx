import React, { useEffect, useState } from 'react'

export default function RecentActivity() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let mounted = true
    async function load() {
      setLoading(true)
      try {
        const res = await fetch('/api/recent_activity')
        if (!res.ok) throw new Error('No recent_activity API')
        const json = await res.json()
        if (!mounted) return
        setItems(json.items || [])
      } catch (err) {
        // fallback mock
        setItems([
          { time: '2026-07-31 09:30', text: 'Bought 100 AAPL @150.00' },
          { time: '2026-07-30 15:45', text: 'Backtest completed: SMA strategy' },
          { time: '2026-07-29 10:12', text: 'Model training finished (RF)' },
        ])
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-md font-medium mb-2">Recent Activity</h3>
      {loading && <div className="text-sm text-gray-500">Loading...</div>}
      <ul className="space-y-2 mt-2 text-sm text-gray-700">
        {items.map((it, i) => (
          <li key={i} className="p-2 border rounded">
            <div className="text-xs text-gray-500">{it.time}</div>
            <div>{it.text}</div>
          </li>
        ))}
      </ul>
    </div>
  )
}
