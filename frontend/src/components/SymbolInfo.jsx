import React, { useEffect, useState } from 'react'

export default function SymbolInfo({ symbol }) {
  const [info, setInfo] = useState(null)

  useEffect(() => {
    if (!symbol) return
    let mounted = true
    async function load() {
      try {
        const res = await fetch(`/api/symbol_info?symbol=${encodeURIComponent(symbol)}`)
        if (!res.ok) throw new Error('No symbol_info API')
        const json = await res.json()
        if (!mounted) return
        setInfo(json)
      } catch (err) {
        setInfo({ symbol, name: `${symbol} Corp`, exchange: 'NASDAQ', sector: 'Technology', description: 'Sample instrument for demo.' })
      }
    }
    load()
    return () => (mounted = false)
  }, [symbol])

  if (!symbol) return null

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-md font-medium mb-2">Symbol</h3>
      <div className="text-sm">
        <div className="font-medium">{info?.symbol}</div>
        <div className="text-xs text-gray-600">{info?.name} • {info?.exchange}</div>
        <div className="mt-2 text-xs text-gray-500">{info?.description}</div>
      </div>
    </div>
  )
}
