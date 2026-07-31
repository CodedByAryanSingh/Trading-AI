import React from 'react'

export default function Footer() {
  return (
    <footer className="bg-white border-t py-3 mt-6">
      <div className="max-w-7xl mx-auto px-6 text-sm text-gray-500">© {new Date().getFullYear()} Trading AI</div>
    </footer>
  )
}
