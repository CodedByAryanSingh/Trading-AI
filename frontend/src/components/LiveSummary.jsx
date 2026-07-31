import React, { useEffect, useState } from 'react'

export default function LiveSummary({ ticker = 'AAPL' }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let mounted = true
    async function load() {
      setLoading(true)
      setError(null)
      try {
        const res = await fetch(`/api/live_price?ticker=${encodeURIComponent(ticker)}`)
        if (!res.ok) throw new Error('No live_price API')
        const json = await res.json()
        if (!mounted) return
        setData(json)
      } catch (err) {
        // fallback mock
        setData({ ticker, price: 150.23, change: -0.42, bid: 150.1, ask: 150.3 })
        setError(err.message || String(err))
      } finally {
        setLoading(false)
      }
    }
    load()
    const iv = setInterval(load, 5000)
    return () => {
      mounted = false
      clearInterval(iv)
    }
  }, [ticker])

  if (loading) return <div className="p-4 bg-white rounded-lg shadow">Loading live summary...</div>

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-md font-medium mb-2">Live Summary</h3>
      {error && <div className="text-xs text-red-500">{error}</div>}
      <div className="flex items-center justify-between">
        <div>
          <div className="text-lg font-semibold">{data.ticker}</div>
          <div className="text-sm text-gray-600">Price: ${data.price}</div>
        </div>
        <div className={`text-lg font-bold ${data.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>{data.change >= 0 ? '+' : ''}{data.change}%</div>
      </div>
      <div className="mt-3 grid grid-cols-2 gap-2 text-sm text-gray-600">
        <div>Bid: {data.bid}</div>
        <div>Ask: {data.ask}</div>
        <div>Volume: {data.volume ?? 'N/A'}</div>
        <div>Spread: {data.ask && data.bid ? (Math.abs(data.ask - data.bid).toFixed(4)) : 'N/A'}</div>
      </div>
    </div>
  )
}
