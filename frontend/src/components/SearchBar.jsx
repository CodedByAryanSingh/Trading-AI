import React, { useEffect, useState } from 'react'

export default function SearchBar({ onSelect }) {
  const [q, setQ] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!q || q.length < 2) {
      setResults([])
      return
    }
    let mounted = true
    const t = setTimeout(async () => {
      setLoading(true)
      try {
        const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`)
        if (!res.ok) throw new Error('Search API not available')
        const json = await res.json()
        if (!mounted) return
        setResults(json.results || [])
      } catch (err) {
        // fallback to simple mock
        const mock = [
          { symbol: q.toUpperCase(), name: `${q.toUpperCase()} Inc.`, exchange: 'NASDAQ', type: 'stock' },
          { symbol: `${q.toUpperCase()}USD`, name: `${q.toUpperCase()} / USD`, exchange: 'BINANCE', type: 'crypto' },
        ]
        setResults(mock)
      } finally {
        setLoading(false)
      }
    }, 300)
    return () => {
      mounted = false
      clearTimeout(t)
    }
  }, [q])

  return (
    <div className="">
      <label className="block text-sm text-gray-600">Symbol Search</label>
      <div className="relative">
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search by symbol or name" className="mt-1 w-full px-3 py-2 border rounded" />
        {loading && <div className="absolute right-2 top-2 text-xs text-gray-500">Searching…</div>}
      </div>
      {results.length > 0 && (
        <ul className="mt-2 border rounded bg-white max-h-48 overflow-auto">
          {results.map((r) => (
            <li key={r.symbol} className="p-2 hover:bg-gray-50 cursor-pointer" onClick={() => onSelect && onSelect(r)}>
              <div className="font-medium">{r.symbol} <span className="text-xs text-gray-500">{r.exchange}</span></div>
              <div className="text-xs text-gray-500">{r.name}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
