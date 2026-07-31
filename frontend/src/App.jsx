import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import MarketAnalysis from './pages/MarketAnalysis'
import AIPredictions from './pages/AIPredictions'
import StrategyResults from './pages/StrategyResults'
import BacktestDashboard from './pages/BacktestDashboard'
import Portfolio from './pages/Portfolio'
import Auth from './pages/Auth'
import Layout from './components/Layout'
import { ThemeProvider } from './contexts/ThemeProvider'
import NotificationsProvider from './components/NotificationsProvider'

export default function App() {
  return (
    <ThemeProvider>
      <NotificationsProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/market" element={<MarketAnalysis />} />
            <Route path="/explorer" element={<MarketExplorer />} />
            <Route path="/ai" element={<AIPredictions />} />
            <Route path="/strategies" element={<StrategyResults />} />
            <Route path="/backtest" element={<BacktestDashboard />} />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/auth" element={<Auth />} />
          </Routes>
        </Layout>
      </NotificationsProvider>
    </ThemeProvider>
  )
}
