import React, { useEffect, useState } from 'react'

export default function AISignals({ ticker = 'AAPL' }) {
  const [signals, setSignals] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let mounted = true
    async function load() {
      setLoading(true)
      setError(null)
      try {
        const res = await fetch(`/api/signals?ticker=${encodeURIComponent(ticker)}`)
        if (!res.ok) throw new Error('No signals API')
        const json = await res.json()
        if (!mounted) return
        setSignals(json.signals || [])
      } catch (err) {
        // fallback example signals
        setSignals([
          { name: 'SMA Crossover', signal: 'BUY', confidence: 0.7 },
          { name: 'RSI', signal: 'HOLD', confidence: 0.0 },
          { name: 'MACD', signal: 'BUY', confidence: 0.4 },
        ])
        setError(err.message || String(err))
      } finally {
        setLoading(false)
      }
    }
    load()
    const iv = setInterval(load, 15000)
    return () => {
      mounted = false
      clearInterval(iv)
    }
  }, [ticker])

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-md font-medium mb-2">AI Signals</h3>
      {loading && <div className="text-sm text-gray-500">Loading AI signals...</div>}
      {error && <div className="text-xs text-red-500">{error}</div>}
      <div className="space-y-2 mt-2">
        {signals.map((s, i) => (
          <div key={`${s.name}-${i}`} className="flex justify-between items-center p-2 border rounded">
            <div>
              <div className="font-medium">{s.name}</div>
              <div className="text-xs text-gray-500">Confidence: {(s.confidence * 100).toFixed(0)}%</div>
            </div>
            <div className={`font-semibold ${s.signal === 'BUY' ? 'text-green-600' : s.signal === 'SELL' ? 'text-red-600' : 'text-gray-600'}`}>{s.signal}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
