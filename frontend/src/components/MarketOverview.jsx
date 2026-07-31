import React, { useEffect, useState } from 'react'

export default function MarketOverview({ tickers = ['AAPL', 'MSFT', 'GOOG', 'BTC-USD'] }) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let mounted = true
    async function load() {
      setLoading(true)
      setError(null)
      try {
        const res = await fetch(`/api/market_overview?tickers=${encodeURIComponent(tickers.join(','))}`)
        if (!res.ok) throw new Error('No overview API')
        const json = await res.json()
        if (!mounted) return
        setData(json.data || [])
      } catch (err) {
        // fallback to lightweight mock data
        const mock = tickers.map((t, i) => ({ ticker: t, price: (100 + i * 10).toFixed(2), change: ((i % 3) - 1) * 0.5 }))
        setData(mock)
        setError(err.message || String(err))
      } finally {
        setLoading(false)
      }
    }
    load()
    return () => (mounted = false)
  }, [tickers])

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-md font-medium mb-2">Market Overview</h3>
      {loading && <div className="text-sm text-gray-500">Loading...</div>}
      {error && <div className="text-sm text-red-500">{error}</div>}
      <div className="grid grid-cols-2 gap-2 mt-2">
        {data.map((row) => (
          <div key={row.ticker} className="p-2 border rounded flex justify-between items-center">
            <div>
              <div className="font-medium">{row.ticker}</div>
              <div className="text-xs text-gray-500">Price: ${row.price}</div>
            </div>
            <div className={`text-sm ${row.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>{row.change >= 0 ? '+' : ''}{row.change}%</div>
          </div>
        ))}
      </div>
    </div>
  )
}
