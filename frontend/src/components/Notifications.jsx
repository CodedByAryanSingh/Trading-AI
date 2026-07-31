import React, { createContext, useContext, useState } from 'react'

const NotificationContext = createContext(null)

export function useNotifications() {
  return useContext(NotificationContext)
}

export function NotificationProvider({ children }) {
  const [messages, setMessages] = useState([])

  function push(message) {
    const id = Date.now() + Math.random()
    setMessages((m) => [...m, { id, message }])
    // auto-remove after 4s
    setTimeout(() => setMessages((m) => m.filter((it) => it.id !== id)), 4000)
  }

  return (
    <NotificationContext.Provider value={{ push }}>
      {children}
      <div className="fixed bottom-4 right-4 space-y-2 z-50">
        {messages.map((m) => (
          <div key={m.id} className="bg-white shadow px-4 py-2 rounded border">{m.message}</div>
        ))}
      </div>
    </NotificationContext.Provider>
  )
}

export default function Notifications() {
  return null // UI is provided by provider; this component kept for compatibility
}
