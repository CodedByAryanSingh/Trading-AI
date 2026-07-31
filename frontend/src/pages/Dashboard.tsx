import React, { useState, useEffect } from 'react'
import Chart from '../components/Chart'

const INTERVALS = ['1d', '1h', '15m', '5m', '1m']
const PERIODS = ['1mo', '3mo', '6mo', '1y']

export default function Dashboard(): JSX.Element {
  const [tickerInput, setTickerInput] = useState<string>('AAPL')
  const [intervalInput, setIntervalInput] = useState<string>('1d')
  const [periodInput, setPeriodInput] = useState<string>('1mo')

  // debounced state to avoid excessive requests
  const [query, setQuery] = useState<{ ticker: string; interval: string; period: string }>({
    ticker: 'AAPL',
    interval: '1d',
    period: '1mo',
  })

  useEffect(() => {
    const t = setTimeout(() => {
      setQuery({ ticker: tickerInput.trim().toUpperCase() || 'AAPL', interval: intervalInput, period: periodInput })
    }, 500)
    return () => clearTimeout(t)
  }, [tickerInput, intervalInput, periodInput])

  return (
    <div className="space-y-6">
      <section className="bg-white rounded-lg shadow p-4">
        <h2 className="text-lg font-medium mb-4">Live Chart</h2>
        <div className="flex gap-4 items-center mb-4">
          <div>
            <label className="block text-sm text-gray-600">Ticker</label>
            <input value={tickerInput} onChange={(e) => setTickerInput(e.target.value)} className="mt-1 px-3 py-2 border rounded" />
          </div>
          <div>
            <label className="block text-sm text-gray-600">Interval</label>
            <select value={intervalInput} onChange={(e) => setIntervalInput(e.target.value)} className="mt-1 px-3 py-2 border rounded">
              {INTERVALS.map((i) => (
                <option key={i} value={i}>{i}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-600">Period</label>
            <select value={periodInput} onChange={(e) => setPeriodInput(e.target.value)} className="mt-1 px-3 py-2 border rounded">
              {PERIODS.map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>
        </div>

        <div style={{ height: 500 }}>
          <Chart ticker={query.ticker} interval={query.interval} period={query.period} />
        </div>
      </section>

      <section className="bg-white rounded-lg shadow p-4">
        <h2 className="text-lg font-medium mb-4">Quick Stats</h2>
        <div className="grid grid-cols-3 gap-4">
          <div className="p-4 border rounded">Equity: <strong>$100,000</strong></div>
          <div className="p-4 border rounded">Positions: <strong>0</strong></div>
          <div className="p-4 border rounded">Open PnL: <strong>$0</strong></div>
        </div>
      </section>
    </div>
  )
}
