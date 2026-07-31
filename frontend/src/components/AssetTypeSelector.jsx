import React from 'react'

export default function AssetTypeSelector({ value = 'stocks', onChange }) {
  const types = [{ key: 'stocks', label: 'Stocks' }, { key: 'crypto', label: 'Crypto' }, { key: 'forex', label: 'Forex' }, { key: 'etf', label: 'ETF' }, { key: 'indices', label: 'Index' }, { key: 'futures', label: 'Futures' }]
  return (
    <div>
      <label className="block text-sm text-gray-600">Asset Type</label>
      <select value={value} onChange={(e) => onChange && onChange(e.target.value)} className="mt-1 px-3 py-2 border rounded">
        {types.map((t) => (
          <option key={t.key} value={t.key}>{t.label}</option>
        ))}
      </select>
    </div>
  )
}
