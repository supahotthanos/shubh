'use client'

import { Minus, TrendingDown, TrendingUp } from 'lucide-react'
import { clsx } from 'clsx'

import { EmptyState } from '@/components/ui/EmptyState'
import { Skeleton } from '@/components/ui/Skeleton'

interface Platform {
  platform_name: string
  platform_slug: string
  total_citations: number
  avg_position: number
  stability_score: number
  trend?: 'up' | 'down' | 'stable'
  trend_value?: number
}

export function PlatformBreakdown({
  platforms,
  isLoading,
}: {
  platforms?: Platform[]
  isLoading?: boolean
}) {
  const total = (platforms ?? []).reduce((acc, p) => acc + (p.total_citations || 0), 0)

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">Platform breakdown</h2>
        <span className="text-sm text-dark-400">{total} total</span>
      </div>
      {isLoading ? (
        <div className="space-y-3 mt-4">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
        </div>
      ) : !platforms || platforms.length === 0 ? (
        <EmptyState title="No platform data yet" description="Run a visibility check on a prompt to populate." />
      ) : (
        <div className="space-y-4">
          {platforms.map((p) => {
            const percentage = total ? ((p.total_citations || 0) / total) * 100 : 0
            const TrendIcon = p.trend === 'up' ? TrendingUp : p.trend === 'down' ? TrendingDown : Minus
            return (
              <div key={p.platform_slug} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-dark-800 rounded-lg flex items-center justify-center text-xs font-bold text-primary-400">
                      {p.platform_name.charAt(0)}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white">{p.platform_name}</p>
                      <p className="text-xs text-dark-500">
                        Avg pos {p.avg_position?.toFixed(1) ?? '—'} · Stability {(p.stability_score ?? 0).toFixed(0)}%
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-white">{p.total_citations}</p>
                    <div
                      className={clsx(
                        'flex items-center gap-1 text-xs',
                        p.trend === 'up' && 'text-green-400',
                        p.trend === 'down' && 'text-red-400',
                        (!p.trend || p.trend === 'stable') && 'text-dark-400',
                      )}
                    >
                      <TrendIcon className="w-3 h-3" />
                      <span>{(p.trend_value ?? 0) > 0 ? '+' : ''}{p.trend_value ?? 0}%</span>
                    </div>
                  </div>
                </div>
                <div className="h-2 bg-dark-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary-500 rounded-full transition-all duration-500"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
