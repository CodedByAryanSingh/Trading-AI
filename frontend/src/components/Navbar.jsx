import React, { useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useTheme } from '../contexts/ThemeProvider'

export default function Navbar() {
  const [openSettings, setOpenSettings] = useState(false)
  const [openProfile, setOpenProfile] = useState(false)
  const navigate = useNavigate()
  const { theme, toggle } = useTheme()

  // In a real app, replace with auth context
  const [isAuthenticated] = useState(false)

  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto py-3 px-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to="/dashboard" className="flex items-center gap-3">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
              <rect width="24" height="24" rx="6" fill="#6366F1" />
              <path d="M6 14l3-6 3 4 3-8 3 12" stroke="#fff" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <span className="text-lg font-semibold text-gray-900">Trading AI</span>
          </Link>

          <nav className="hidden lg:flex gap-4 ml-6">
            <NavLink to="/dashboard" className={({isActive}) => `text-sm ${isActive ? 'text-indigo-600' : 'text-gray-600'} hover:text-gray-900`}>Dashboard</NavLink>
            <NavLink to="/market" className={({isActive}) => `text-sm ${isActive ? 'text-indigo-600' : 'text-gray-600'} hover:text-gray-900`}>Markets</NavLink>
            <NavLink to="/explorer" className={({isActive}) => `text-sm ${isActive ? 'text-indigo-600' : 'text-gray-600'} hover:text-gray-900`}>Explorer</NavLink>
            <NavLink to="/market" className={({isActive}) => `text-sm ${isActive ? 'text-indigo-600' : 'text-gray-600'} hover:text-gray-900`}>Analysis</NavLink>
            <NavLink to="/strategies" className={({isActive}) => `text-sm ${isActive ? 'text-indigo-600' : 'text-gray-600'} hover:text-gray-900`}>Strategies</NavLink>
            <NavLink to="/backtest" className={({isActive}) => `text-sm ${isActive ? 'text-indigo-600' : 'text-gray-600'} hover:text-gray-900`}>Backtesting</NavLink>
            <NavLink to="/portfolio" className={({isActive}) => `text-sm ${isActive ? 'text-indigo-600' : 'text-gray-600'} hover:text-gray-900`}>Portfolio</NavLink>
            <NavLink to="/news" className={({isActive}) => `text-sm ${isActive ? 'text-indigo-600' : 'text-gray-600'} hover:text-gray-900`}>News</NavLink>
          </nav>
        </div>

        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/watchlist')} className="hidden sm:inline-flex items-center px-3 py-2 text-sm rounded hover:bg-gray-50">
            Watchlist
          </button>

          <button onClick={() => navigate('/portfolio')} className="hidden sm:inline-flex items-center px-3 py-2 text-sm rounded hover:bg-gray-50">
            Portfolio
          </button>

          <button onClick={() => toggle()} title={`Toggle ${theme === 'dark' ? 'light' : 'dark'} theme`} className="px-2 py-1 rounded hover:bg-gray-50">
            {theme === 'dark' ? '🌙' : '☀️'}
          </button>

          <div className="relative">
            <button onClick={() => setOpenSettings((s) => !s)} className="px-2 py-1 rounded hover:bg-gray-50 text-sm">Settings ▾</button>
            {openSettings && (
              <div className="absolute right-0 mt-2 w-48 bg-white border rounded shadow p-2 z-40">
                <Link to="/settings/profile" className="block px-2 py-1 text-sm hover:bg-gray-50">Profile</Link>
                <Link to="/settings/account" className="block px-2 py-1 text-sm hover:bg-gray-50">Account</Link>
                <Link to="/settings/preferences" className="block px-2 py-1 text-sm hover:bg-gray-50">Preferences</Link>
              </div>
            )}
          </div>

          <div className="relative">
            {isAuthenticated ? (
              <>
                <button onClick={() => setOpenProfile((s) => !s)} className="flex items-center gap-2 px-2 py-1 rounded hover:bg-gray-50">
                  <img src="/avatar.png" alt="Profile" className="w-7 h-7 rounded-full" />
                  <span className="hidden sm:inline text-sm">Me</span>
                </button>
                {openProfile && (
                  <div className="absolute right-0 mt-2 w-48 bg-white border rounded shadow p-2 z-40">
                    <Link to="/profile" className="block px-2 py-1 text-sm hover:bg-gray-50">My Profile</Link>
                    <Link to="/settings" className="block px-2 py-1 text-sm hover:bg-gray-50">Settings</Link>
                    <button onClick={() => {/* sign out logic */}} className="w-full text-left px-2 py-1 text-sm hover:bg-gray-50">Sign out</button>
                  </div>
                )}
              </>
            ) : (
              <Link to="/auth" className="px-3 py-2 bg-indigo-600 text-white rounded text-sm">Sign in</Link>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
