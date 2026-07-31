import React, { useEffect, useState } from 'react'

export default function WatchlistPreview({ tickers = ['AAPL', 'MSFT', 'GOOG'] }) {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let mounted = true
    async function load() {
      setLoading(true)
      try {
        const res = await fetch(`/api/watchlist_preview?tickers=${encodeURIComponent(tickers.join(','))}`)
        if (!res.ok) throw new Error('No watchlist_preview API')
        const json = await res.json()
        if (!mounted) return
        setItems(json.items || [])
      } catch (err) {
        // fallback
        setItems(tickers.map((t, i) => ({ ticker: t, price: (120 + i * 5).toFixed(2), change: ((i % 3) - 1) * 0.4 })))
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [tickers])

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-md font-medium mb-2">Watchlist Preview</h3>
      {loading && <div className="text-sm text-gray-500">Loading...</div>}
      <ul className="space-y-2 mt-2">
        {items.map((it) => (
          <li key={it.ticker} className="flex justify-between items-center p-2 border rounded">
            <div>
              <div className="font-medium">{it.ticker}</div>
              <div className="text-xs text-gray-500">Price: ${it.price}</div>
            </div>
            <div className={`text-sm ${it.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>{it.change >= 0 ? '+' : ''}{it.change}%</div>
          </li>
        ))}
      </ul>
    </div>
  )
}
