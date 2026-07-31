import React, { useEffect, useRef } from 'react'
import { createChart } from 'lightweight-charts'

/**
 * Simple candlestick chart using lightweight-charts.
 * Expects to be rendered inside a container with explicit height.
 */
export default function Chart() {
  const ref = useRef(null)
  const chartRef = useRef(null)
  const candleSeriesRef = useRef(null)
  const volumeSeriesRef = useRef(null)

  useEffect(() => {
    if (!ref.current) return

    const chart = createChart(ref.current, {
      width: ref.current.clientWidth,
      height: ref.current.clientHeight,
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

    // sample data (OHLC) - replace with real API data
    const candles = [
      { time: '2024-07-01', open: 100, high: 105, low: 98, close: 104 },
      { time: '2024-07-02', open: 104, high: 107, low: 103, close: 106 },
      { time: '2024-07-03', open: 106, high: 110, low: 105, close: 108 },
      { time: '2024-07-04', open: 108, high: 112, low: 107, close: 111 },
      { time: '2024-07-05', open: 111, high: 115, low: 110, close: 114 },
    ]

    const volumes = [
      { time: '2024-07-01', value: 1200, color: 'rgba(0, 150, 136, 0.8)' },
      { time: '2024-07-02', value: 900, color: 'rgba(0, 150, 136, 0.8)' },
      { time: '2024-07-03', value: 1500, color: 'rgba(0, 150, 136, 0.8)' },
      { time: '2024-07-04', value: 2000, color: 'rgba(244, 67, 54, 0.8)' },
      { time: '2024-07-05', value: 1800, color: 'rgba(0, 150, 136, 0.8)' },
    ]

    candleSeries.setData(candles)
    volumeSeries.setData(volumes)

    const handleResize = () => {
      if (!ref.current) return
      chart.applyOptions({ width: ref.current.clientWidth })
    }
    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [])

  return <div ref={ref} className="w-full h-full" />
}
