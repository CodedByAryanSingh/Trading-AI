import React, { useEffect, useRef, useState } from 'react'
import { createChart, IChartApi } from 'lightweight-charts'

type Candle = { time: string | number; open: number; high: number; low: number; close: number }
type Volume = { time: string | number; value: number; color?: string }

export default function Chart({ ticker = 'AAPL', interval = '1d', period = '1mo' }: { ticker?: string; interval?: string; period?: string }): JSX.Element {
  const ref = useRef<HTMLDivElement | null>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const candleSeriesRef = useRef<any>(null)
  const volumeSeriesRef = useRef<any>(null)
  const [loading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    if (!ref.current) return
    const container = ref.current
    const chart = createChart(container, {
      width: container.clientWidth,
      height: container.clientHeight,
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

    const handleResize = () => {
      if (!ref.current) return
      chart.applyOptions({ width: ref.current.clientWidth })
    }
    window.addEventListener('resize', handleResize)

    // fetch OHLCV from backend
    const fetchData = async () => {
      setLoading(true)
      try {
        const resp = await fetch(`/api/ohlcv?ticker=${encodeURIComponent(ticker)}&interval=${encodeURIComponent(interval)}&period=${encodeURIComponent(period)}`)
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
        const payload = await resp.json()
        const candles: Candle[] = payload.candles
        const volumes: Volume[] = payload.volumes
        // set chart data
        candleSeries.setData(candles)
        // map volumes to include color based on candle close vs open
        const minLen = Math.min(candles.length, volumes.length)
        const volColored = volumes.slice(0, minLen).map((v, i) => {
          const c = candles[i]
          const color = c && c.close >= c.open ? 'rgba(0,150,136,0.8)' : 'rgba(244,67,54,0.8)'
          return { ...v, color }
        })
        volumeSeries.setData(volColored)
      } catch (err) {
        // fallback to sample data on error
        console.error('Failed to fetch OHLCV', err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [ticker, interval, period])

  return (
    <div className="w-full h-full relative">
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-white/60 z-10">Loading chart…</div>
      )}
      <div ref={ref} className="w-full h-full" />
    </div>
  )
}
