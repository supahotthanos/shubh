'use client'

import { Bell, RefreshCw, Calendar } from 'lucide-react'
import { useState } from 'react'

export function DashboardHeader() {
  const [period, setPeriod] = useState('30d')

  return (
    <header className="sticky top-0 z-10 bg-dark-900/80 backdrop-blur-sm border-b border-dark-800 px-6 py-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-sm text-dark-400">
            Track your AI visibility across all platforms
          </p>
        </div>

        <div className="flex items-center gap-4">
          {/* Period Selector */}
          <div className="flex items-center gap-2 bg-dark-800 rounded-lg p-1">
            {['7d', '30d', '60d', '90d'].map((p) => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  period === p
                    ? 'bg-primary-600 text-white'
                    : 'text-dark-400 hover:text-white'
                }`}
              >
                {p}
              </button>
            ))}
          </div>

          {/* Refresh Button */}
          <button className="btn btn-secondary flex items-center gap-2">
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>

          {/* Notifications */}
          <button className="relative p-2 rounded-lg hover:bg-dark-800 transition-colors">
            <Bell className="w-5 h-5 text-dark-400" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>

          {/* User Avatar */}
          <div className="w-9 h-9 bg-primary-600 rounded-full flex items-center justify-center">
            <span className="text-sm font-medium text-white">JD</span>
          </div>
        </div>
      </div>
    </header>
  )
}
