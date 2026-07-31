import React, { useState, useEffect } from 'react'
import Chart from '../components/Chart'
import MarketOverview from '../components/MarketOverview'
import LiveSummary from '../components/LiveSummary'
import AISignals from '../components/AISignals'
import PerformanceWidgets from '../components/PerformanceWidgets'
import RecentActivity from '../components/RecentActivity'

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
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
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

          <PerformanceWidgets />
        </div>

        <div className="space-y-6">
          <MarketOverview tickers={[query.ticker, 'MSFT', 'GOOG', 'BTC-USD']} />
          <LiveSummary ticker={query.ticker} />
          <AISignals ticker={query.ticker} />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <RecentSignals />
        </div>
        <div>
          <WatchlistPreview tickers={[query.ticker, 'MSFT', 'GOOG']} />
          <OpenPositions />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <MarketNews />
        </div>
        <div>
          <PortfolioSummary />
        </div>
      </div>

      <RecentActivity />
    </div>
  )
}
