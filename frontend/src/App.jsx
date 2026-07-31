import React from 'react'
import Chart from './components/Chart'

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto py-4 px-6">
          <h1 className="text-2xl font-semibold text-gray-900">Trading AI Dashboard</h1>
        </div>
      </header>
      <main className="flex-1 p-6 max-w-7xl mx-auto">
        <section className="bg-white rounded-lg shadow p-4">
          <h2 className="text-lg font-medium mb-4">Live Chart</h2>
          <div style={{ height: 500 }}>
            <Chart />
          </div>
        </section>
      </main>
      <footer className="bg-white border-t py-3">
        <div className="max-w-7xl mx-auto px-6 text-sm text-gray-500">© Trading AI</div>
      </footer>
    </div>
  )
}
