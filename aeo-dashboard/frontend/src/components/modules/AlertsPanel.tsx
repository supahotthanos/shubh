'use client'

import { AlertCircle, AlertTriangle, ChevronRight, Info } from 'lucide-react'
import Link from 'next/link'
import { clsx } from 'clsx'

import { EmptyState } from '@/components/ui/EmptyState'
import { Skeleton } from '@/components/ui/Skeleton'

const styles: Record<string, { bg: string; border: string; icon: any; iconColor: string }> = {
  critical: { bg: 'bg-red-500/10', border: 'border-red-500/20', icon: AlertCircle, iconColor: 'text-red-400' },
  warning: { bg: 'bg-yellow-500/10', border: 'border-yellow-500/20', icon: AlertTriangle, iconColor: 'text-yellow-400' },
  info: { bg: 'bg-blue-500/10', border: 'border-blue-500/20', icon: Info, iconColor: 'text-blue-400' },
}

interface AlertItem {
  id: string
  severity: string
  title: string
  description: string
  action_url?: string
  created_at?: string
}

export function AlertsPanel({ data, isLoading }: { data?: any; isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="card h-full">
        <div className="card-header">
          <h2 className="card-title">Alerts</h2>
        </div>
        <div className="space-y-3 mt-2">
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
        </div>
      </div>
    )
  }
  const all: AlertItem[] = [
    ...(data?.critical ?? []),
    ...(data?.warnings ?? []),
    ...(data?.info ?? []),
  ]

  return (
    <div className="card h-full">
      <div className="card-header">
        <h2 className="card-title">Alerts</h2>
        {all.length > 0 && <span className="badge badge-danger">{all.length}</span>}
      </div>
      {all.length === 0 ? (
        <EmptyState title="All clear" description="No alerts for the current client." />
      ) : (
        <div className="space-y-3 mt-2 max-h-80 overflow-y-auto">
          {all.map((alert) => {
            const style = styles[alert.severity] ?? styles.info
            const Icon = style.icon
            return (
              <div key={alert.id} className={clsx('p-3 rounded-lg border', style.bg, style.border)}>
                <div className="flex gap-3">
                  <Icon className={clsx('w-5 h-5 mt-0.5 flex-shrink-0', style.iconColor)} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-white">{alert.title}</p>
                    <p className="text-xs text-dark-400 mt-1">{alert.description}</p>
                    {alert.action_url && (
                      <Link
                        href={alert.action_url}
                        className="mt-2 inline-flex items-center gap-1 text-xs text-primary-400 hover:text-primary-300"
                      >
                        View <ChevronRight className="w-3 h-3" />
                      </Link>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
