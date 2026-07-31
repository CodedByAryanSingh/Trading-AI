import React, { useEffect, useState } from 'react'

export default function MarketNews() {
  const [news, setNews] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let mounted = true
    async function load() {
      setLoading(true)
      try {
        const res = await fetch('/api/news')
        if (!res.ok) throw new Error('No news API')
        const json = await res.json()
        if (!mounted) return
        setNews(json.articles || [])
      } catch (err) {
        setNews([
          { time: '2026-07-31', title: 'Market opens higher as tech leads', source: 'Bloomberg' },
          { time: '2026-07-30', title: 'Fed minutes signal cautious stance', source: 'Reuters' },
        ])
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-md font-medium mb-2">Market News</h3>
      {loading && <div className="text-sm text-gray-500">Loading...</div>}
      <ul className="space-y-2 mt-2 text-sm">
        {news.map((n, i) => (
          <li key={i} className="p-2 border rounded">
            <div className="text-xs text-gray-500">{n.time} • {n.source}</div>
            <div className="font-medium">{n.title}</div>
          </li>
        ))}
      </ul>
    </div>
  )
}
