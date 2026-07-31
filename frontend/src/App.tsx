import React from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import BacktestResults from './pages/BacktestResults'

export default function App(): JSX.Element {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto py-4 px-6 flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-gray-900">Trading AI Dashboard</h1>
          <nav className="space-x-4">
            <Link to="/" className="text-sm text-gray-600 hover:text-gray-900">Dashboard</Link>
            <Link to="/backtest" className="text-sm text-gray-600 hover:text-gray-900">Backtest Results</Link>
          </nav>
        </div>
      </header>
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/backtest" element={<BacktestResults />} />
        </Routes>
      </main>
      <footer className="bg-white border-t py-3">
        <div className="max-w-7xl mx-auto px-6 text-sm text-gray-500">© Trading AI</div>
      </footer>
    </div>
  )
}
