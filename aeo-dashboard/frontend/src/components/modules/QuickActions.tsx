'use client'

import { ArrowRight, Code, RefreshCw, Target } from 'lucide-react'
import { clsx } from 'clsx'
import type { ReactNode } from 'react'

import { EmptyState } from '@/components/ui/EmptyState'
import { Skeleton } from '@/components/ui/Skeleton'

const iconByType: Record<string, ReactNode> = {
  content_refresh: <RefreshCw className="w-5 h-5" />,
  schema_optimization: <Code className="w-5 h-5" />,
  keyword_expansion: <Target className="w-5 h-5" />,
}

const impactColors: Record<string, string> = {
  high: 'text-green-400 bg-green-400/10',
  medium: 'text-yellow-400 bg-yellow-400/10',
  low: 'text-dark-400 bg-dark-700',
}

export function QuickActions({ data, isLoading }: { data?: any; isLoading?: boolean }) {
  const actions: any[] = data?.actions ?? []

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h2 className="card-title">Quick actions</h2>
          <p className="text-sm text-dark-400 mt-1">Prioritized tasks based on your current data</p>
        </div>
      </div>
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          <Skeleton className="h-28" />
          <Skeleton className="h-28" />
          <Skeleton className="h-28" />
        </div>
      ) : actions.length === 0 ? (
        <EmptyState title="Nothing urgent" description="Your data looks healthy right now." />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          {actions.map((a) => (
            <div
              key={a.id}
              className="p-4 bg-dark-800 rounded-lg border border-dark-700 hover:border-primary-500/50 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className={clsx('p-2 rounded-lg', impactColors[a.estimated_impact] ?? impactColors.medium)}>
                  {iconByType[a.action_type] ?? <Target className="w-5 h-5" />}
                </div>
                <span className={clsx('badge text-xs', impactColors[a.estimated_impact] ?? impactColors.medium)}>
                  {a.estimated_impact} impact
                </span>
              </div>
              <h3 className="mt-4 text-sm font-semibold text-white">{a.title}</h3>
              <p className="mt-1 text-xs text-dark-400">{a.description}</p>
              <div className="mt-4 flex items-center gap-2 text-xs text-primary-400">
                Take action <ArrowRight className="w-3 h-3" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
