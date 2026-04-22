'use client'

import { FileText, MessageSquare, Minus, Target, TrendingDown, TrendingUp, Users } from 'lucide-react'
import { clsx } from 'clsx'
import type { ReactNode } from 'react'

import { Skeleton } from '@/components/ui/Skeleton'

interface KPICardProps {
  title: string
  value: string | number
  change?: number
  icon: ReactNode
  trend?: 'up' | 'down' | 'stable'
  subtitle?: string
}

function KPICard({ title, value, change, icon, trend, subtitle }: KPICardProps) {
  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus
  return (
    <div className="card">
      <div className="flex items-start justify-between">
        <div className="p-2 bg-primary-600/10 rounded-lg">{icon}</div>
        {change !== undefined && (
          <div
            className={clsx(
              'flex items-center gap-1 text-sm',
              trend === 'up' && 'text-green-400',
              trend === 'down' && 'text-red-400',
              trend === 'stable' && 'text-dark-400',
            )}
          >
            <TrendIcon className="w-4 h-4" />
            <span>
              {change > 0 ? '+' : ''}
              {change}%
            </span>
          </div>
        )}
      </div>
      <div className="mt-4">
        <p className="stat-value">{value}</p>
        <p className="stat-label mt-1">{title}</p>
        {subtitle && <p className="text-xs text-dark-500 mt-1">{subtitle}</p>}
      </div>
    </div>
  )
}

export function KPICards({ metrics, isLoading }: { metrics: any; isLoading?: boolean }) {
  if (isLoading || !metrics) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="card">
            <Skeleton className="h-24 w-full" />
          </div>
        ))}
      </div>
    )
  }

  const trend = (t: any): 'up' | 'down' | 'stable' => t?.trend ?? 'stable'
  const kpis = [
    {
      title: 'Total AI Citations',
      value: metrics.total_citations ?? 0,
      change: metrics.citations_trend?.change_percentage ?? 0,
      trend: trend(metrics.citations_trend),
      icon: <MessageSquare className="w-5 h-5 text-primary-400" />,
      subtitle: `${metrics.citations_trend?.change ?? 0} vs prior period`,
    },
    {
      title: 'Citation Stability',
      value: `${(metrics.citation_stability_score ?? 0).toFixed(1)}%`,
      change: metrics.stability_trend?.change_percentage ?? 0,
      trend: trend(metrics.stability_trend),
      icon: <Target className="w-5 h-5 text-primary-400" />,
      subtitle: 'Consistency across checks',
    },
    {
      title: 'RRF Visibility',
      value: (metrics.rrf_visibility_score ?? 0).toFixed(4),
      change: metrics.rrf_trend?.change_percentage ?? 0,
      trend: trend(metrics.rrf_trend),
      icon: <TrendingUp className="w-5 h-5 text-primary-400" />,
      subtitle: `${metrics.keywords_meeting_threshold ?? 0}/${metrics.keywords_total ?? 0} keywords at τ`,
    },
    {
      title: 'Content Freshness',
      value: metrics.content_freshness_grade ?? '—',
      icon: <FileText className="w-5 h-5 text-primary-400" />,
      subtitle: `${metrics.pages_needing_refresh ?? 0} pages need refresh`,
    },
    {
      title: 'Prompt Coverage',
      value: `${(metrics.prompt_coverage_percentage ?? 0).toFixed(1)}%`,
      icon: <Target className="w-5 h-5 text-primary-400" />,
      subtitle: `${metrics.prompts_visible ?? 0}/${metrics.prompts_total ?? 0} prompts visible`,
    },
    {
      title: 'Competitive Position',
      value: `#${metrics.competitive_position ?? 1}`,
      icon: <Users className="w-5 h-5 text-primary-400" />,
      subtitle: `${(metrics.share_of_voice ?? 0).toFixed(1)}% share of voice`,
    },
  ]

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
      {kpis.map((kpi) => (
        <KPICard key={kpi.title} {...kpi} />
      ))}
    </div>
  )
}
