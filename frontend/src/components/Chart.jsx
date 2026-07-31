import React, { useEffect, useRef, useState } from 'react'
import { createChart } from 'lightweight-charts'

export default function Chart({ ticker = 'AAPL', interval = '1d', period = '1mo' }) {
  const ref = useRef(null)
  const chartRef = useRef(null)
  const candleSeriesRef = useRef(null)
  const volumeSeriesRef = useRef(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!ref.current) return

    const chart = createChart(ref.current, {
      width: ref.current.clientWidth,
      height: ref.current.clientHeight || 500,
      layout: {
        backgroundColor: '#ffffff',
        textColor: '#333',
      },
      grid: {
        vertLines: { color: '#eee' },
        horzLines: { color: '#eee' },
      },
      rightPriceScale: { borderVisible: false },
      timeScale: { borderVisible: false },
    })

    const candleSeries = chart.addCandlestickSeries()
    const volumeSeries = chart.addHistogramSeries({
      priceFormat: { type: 'volume' },
      scaleMargins: { top: 0.8, bottom: 0 },
    })

    candleSeriesRef.current = candleSeries
    volumeSeriesRef.current = volumeSeries
    chartRef.current = chart

    let mounted = true

    async function load() {
      setLoading(true)
      setError(null)
      try {
        const res = await fetch(`/api/ohlcv?ticker=${encodeURIComponent(ticker)}&interval=${encodeURIComponent(interval)}&period=${encodeURIComponent(period)}`)
        if (!res.ok) throw new Error('Failed to fetch')
        const data = await res.json()
        const candles = data.candles || []
        const volumes = data.volumes || []
        if (!mounted) return
        candleSeries.setData(candles)
        const minLen = Math.min(candles.length, volumes.length)
        const volColored = volumes.slice(0, minLen).map((v, i) => {
          const c = candles[i]
          const color = c && c.close >= c.open ? 'rgba(0,150,136,0.8)' : 'rgba(244,67,54,0.8)'
          return { ...v, color }
        })
        volumeSeries.setData(volColored)
      } catch (err) {
        console.error(err)
        setError(err.message || String(err))
      } finally {
        setLoading(false)
      }
    }

    load()

    const handleResize = () => {
      if (!ref.current) return
      chart.applyOptions({ width: ref.current.clientWidth })
    }
    window.addEventListener('resize', handleResize)

    return () => {
      mounted = false
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [ticker, interval, period])

  return (
    <div className="h-full">
      {loading && <div className="p-4">Loading chart...</div>}
      {error && <div className="p-4 text-red-600">Error: {error}</div>}
      <div ref={ref} style={{ width: '100%', height: 500 }} />
    </div>
  )
}
