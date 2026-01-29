'use client'

import { AlertTriangle, AlertCircle, Info, X, ChevronRight } from 'lucide-react'
import { clsx } from 'clsx'

interface Alert {
  id: string
  type: 'critical' | 'warning' | 'info'
  title: string
  description: string
  time: string
  actionUrl?: string
}

const alerts: Alert[] = [
  {
    id: '1',
    type: 'critical',
    title: 'Content Critically Outdated',
    description: "Page 'Best SEO Tools 2024' hasn't been updated in 14 months",
    time: '2 hours ago',
    actionUrl: '/content/123',
  },
  {
    id: '2',
    type: 'warning',
    title: 'Lost Citation on High-Value Prompt',
    description: "No longer cited for 'best project management software'",
    time: '6 hours ago',
    actionUrl: '/prompts/456',
  },
  {
    id: '3',
    type: 'warning',
    title: 'Competitor Published New Listicle',
    description: "CompetitorX published 'Top 10 Tools' featuring themselves at #1",
    time: '1 day ago',
    actionUrl: '/competitors/789',
  },
  {
    id: '4',
    type: 'info',
    title: 'RRF Score Improved',
    description: "Keyword 'crm software' now meets citation threshold",
    time: '2 days ago',
    actionUrl: '/keywords/101',
  },
]

const alertStyles = {
  critical: {
    bg: 'bg-red-500/10',
    border: 'border-red-500/20',
    icon: AlertCircle,
    iconColor: 'text-red-400',
  },
  warning: {
    bg: 'bg-yellow-500/10',
    border: 'border-yellow-500/20',
    icon: AlertTriangle,
    iconColor: 'text-yellow-400',
  },
  info: {
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/20',
    icon: Info,
    iconColor: 'text-blue-400',
  },
}

export function AlertsPanel() {
  return (
    <div className="card h-full">
      <div className="card-header">
        <h2 className="card-title">Alerts</h2>
        <span className="badge badge-danger">{alerts.length} new</span>
      </div>

      <div className="space-y-3 mt-2 max-h-80 overflow-y-auto">
        {alerts.map((alert) => {
          const style = alertStyles[alert.type]
          const Icon = style.icon

          return (
            <div
              key={alert.id}
              className={clsx(
                'p-3 rounded-lg border cursor-pointer hover:brightness-110 transition-all',
                style.bg,
                style.border
              )}
            >
              <div className="flex gap-3">
                <Icon className={clsx('w-5 h-5 mt-0.5 flex-shrink-0', style.iconColor)} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-sm font-medium text-white">{alert.title}</p>
                    <button className="text-dark-500 hover:text-white">
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                  <p className="text-xs text-dark-400 mt-1">{alert.description}</p>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-xs text-dark-500">{alert.time}</span>
                    {alert.actionUrl && (
                      <button className="flex items-center gap-1 text-xs text-primary-400 hover:text-primary-300">
                        View <ChevronRight className="w-3 h-3" />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      <button className="mt-4 w-full text-sm text-dark-400 hover:text-white transition-colors">
        View all alerts
      </button>
    </div>
  )
}
