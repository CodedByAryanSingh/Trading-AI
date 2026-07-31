import React from 'react'

export default function TimeframeSelector({ value = '1d', onChange }) {
  const options = ['1m','5m','15m','1h','4h','1d','1w']
  return (
    <div>
      <label className="block text-sm text-gray-600">Timeframe</label>
      <select value={value} onChange={(e) => onChange && onChange(e.target.value)} className="mt-1 px-3 py-2 border rounded">
        {options.map((o) => (
          <option key={o} value={o}>{o}</option>
        ))}
      </select>
    </div>
  )
}
