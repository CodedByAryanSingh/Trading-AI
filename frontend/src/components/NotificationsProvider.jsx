import React from 'react'
import { NotificationProvider } from './Notifications'

export default function NotificationsProvider({ children }) {
  return <NotificationProvider>{children}</NotificationProvider>
}
