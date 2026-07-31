import React, { useState } from 'react'
import SearchBar from '../components/SearchBar'
import ExchangeSelector from '../components/ExchangeSelector'
import AssetTypeSelector from '../components/AssetTypeSelector'
import TimeframeSelector from '../components/TimeframeSelector'
import SymbolInfo from '../components/SymbolInfo'
import Chart from '../components/Chart'
import LiveSummary from '../components/LiveSummary'

export default function MarketExplorer() {
  const [symbol, setSymbol] = useState('AAPL')
  const [exchange, setExchange] = useState('NASDAQ')
  const [assetType, setAssetType] = useState('stocks')
  const [timeframe, setTimeframe] = useState('1d')

  function onSelectSymbol(s) {
    setSymbol(s.symbol)
    if (s.exchange) setExchange(s.exchange)
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="md:col-span-2">
                <SearchBar onSelect={onSelectSymbol} />
              </div>
              <div className="flex gap-2">
                <ExchangeSelector value={exchange} onChange={setExchange} />
                <AssetTypeSelector value={assetType} onChange={setAssetType} />
                <TimeframeSelector value={timeframe} onChange={setTimeframe} />
              </div>
            </div>

            <SymbolInfo symbol={symbol} />

            <div style={{ height: 420 }} className="mt-4">
              <Chart ticker={symbol} interval={timeframe} period={timeframe === '1d' ? '3mo' : '1mo'} />
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <LiveSummary ticker={symbol} />
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-md font-medium mb-2">Volume</h3>
            <p className="text-sm text-gray-600">Volume and liquidity details will be shown here (requires provider support).</p>
          </div>
        </div>
      </div>
    </div>
  )
}
