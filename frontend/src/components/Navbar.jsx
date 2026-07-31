import React from 'react'
import { Link } from 'react-router-dom'

export default function Navbar() {
  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto py-4 px-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-semibold text-gray-900">Trading AI</h1>
          <nav className="hidden md:flex gap-3">
            <Link to="/dashboard" className="text-sm text-gray-600 hover:text-gray-900">Dashboard</Link>
            <Link to="/market" className="text-sm text-gray-600 hover:text-gray-900">Market</Link>
            <Link to="/ai" className="text-sm text-gray-600 hover:text-gray-900">AI</Link>
            <Link to="/strategies" className="text-sm text-gray-600 hover:text-gray-900">Strategies</Link>
          </nav>
        </div>
        <div>
          <Link to="/auth" className="px-3 py-2 bg-indigo-600 text-white rounded text-sm">Sign in</Link>
        </div>
      </div>
    </header>
  )
}
