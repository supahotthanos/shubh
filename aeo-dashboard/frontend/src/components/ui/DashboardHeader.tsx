'use client'

import { Bell, RefreshCw, User } from 'lucide-react'
import type { ReactNode } from 'react'

import { useAuthStore } from '@/stores/authStore'

interface Props {
  title?: string
  description?: string
  right?: ReactNode
}

export function DashboardHeader({ title = 'Dashboard', description, right }: Props) {
  const { user } = useAuthStore()
  const initials = (user?.full_name || user?.email || 'U').slice(0, 2).toUpperCase()

  return (
    <header className="sticky top-0 z-10 bg-dark-950/80 backdrop-blur-sm border-b border-dark-800 px-6 py-4">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white">{title}</h1>
          {description && <p className="text-sm text-dark-400 mt-1">{description}</p>}
        </div>
        <div className="flex items-center gap-3">
          {right}
          <button className="relative p-2 rounded-lg hover:bg-dark-800" aria-label="Notifications">
            <Bell className="w-5 h-5 text-dark-400" />
          </button>
          <div
            className="w-9 h-9 bg-primary-600 rounded-full flex items-center justify-center"
            aria-label="User avatar"
          >
            {user ? (
              <span className="text-sm font-medium text-white">{initials}</span>
            ) : (
              <User className="w-4 h-4" />
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
