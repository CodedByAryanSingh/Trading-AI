import React from 'react'

export default function ExchangeSelector({ value = 'NASDAQ', onChange }) {
  const exchanges = ['NASDAQ', 'NYSE', 'BINANCE', 'COINBASE', 'FOREX']
  return (
    <div>
      <label className="block text-sm text-gray-600">Exchange</label>
      <select value={value} onChange={(e) => onChange && onChange(e.target.value)} className="mt-1 px-3 py-2 border rounded">
        {exchanges.map((ex) => (
          <option key={ex} value={ex}>{ex}</option>
        ))}
      </select>
    </div>
  )
}
