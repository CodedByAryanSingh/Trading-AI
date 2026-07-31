import React from 'react'
import { NavLink } from 'react-router-dom'

const links = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/market', label: 'Market' },
  { to: '/ai', label: 'AI' },
  { to: '/strategies', label: 'Strategies' },
  { to: '/backtest', label: 'Backtest' },
  { to: '/portfolio', label: 'Portfolio' },
]

export default function Sidebar() {
  return (
    <aside className="w-64 bg-white border-r hidden md:block">
      <div className="p-4">
        <nav className="space-y-2">
          {links.map((l) => (
            <NavLink key={l.to} to={l.to} className={({isActive}) => `block px-3 py-2 rounded ${isActive ? 'bg-indigo-50 text-indigo-700' : 'text-gray-700 hover:bg-gray-50'}`}>
              {l.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </aside>
  )
}
