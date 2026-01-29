'use client'

import { TrendingUp, TrendingDown, Minus, MessageSquare, Target, FileText, Users } from 'lucide-react'
import { clsx } from 'clsx'

interface KPICardProps {
  title: string
  value: string | number
  change?: number
  changeLabel?: string
  icon: React.ReactNode
  trend?: 'up' | 'down' | 'stable'
  subtitle?: string
}

function KPICard({ title, value, change, changeLabel, icon, trend, subtitle }: KPICardProps) {
  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus

  return (
    <div className="card">
      <div className="flex items-start justify-between">
        <div className="p-2 bg-primary-600/10 rounded-lg">
          {icon}
        </div>
        {change !== undefined && (
          <div className={clsx(
            'flex items-center gap-1 text-sm',
            trend === 'up' && 'text-green-400',
            trend === 'down' && 'text-red-400',
            trend === 'stable' && 'text-dark-400'
          )}>
            <TrendIcon className="w-4 h-4" />
            <span>{change > 0 ? '+' : ''}{change}%</span>
          </div>
        )}
      </div>

      <div className="mt-4">
        <p className="stat-value">{value}</p>
        <p className="stat-label mt-1">{title}</p>
        {subtitle && (
          <p className="text-xs text-dark-500 mt-1">{subtitle}</p>
        )}
      </div>
    </div>
  )
}

export function KPICards() {
  const kpis = [
    {
      title: 'Total AI Citations',
      value: '142',
      change: 19.3,
      trend: 'up' as const,
      icon: <MessageSquare className="w-5 h-5 text-primary-400" />,
      subtitle: '23 new this month',
    },
    {
      title: 'Citation Stability',
      value: '78.5%',
      change: 3.0,
      trend: 'up' as const,
      icon: <Target className="w-5 h-5 text-primary-400" />,
      subtitle: 'Consistency across checks',
    },
    {
      title: 'RRF Visibility Score',
      value: '0.024',
      change: 14.3,
      trend: 'up' as const,
      icon: <TrendingUp className="w-5 h-5 text-primary-400" />,
      subtitle: '18/25 keywords at threshold',
    },
    {
      title: 'Content Freshness',
      value: 'B',
      change: 0,
      trend: 'stable' as const,
      icon: <FileText className="w-5 h-5 text-primary-400" />,
      subtitle: '4 pages need refresh',
    },
    {
      title: 'Prompt Coverage',
      value: '55.3%',
      change: 8.2,
      trend: 'up' as const,
      icon: <Target className="w-5 h-5 text-primary-400" />,
      subtitle: '47 of 85 prompts visible',
    },
    {
      title: 'Competitive Position',
      value: '#2',
      change: 0,
      trend: 'stable' as const,
      icon: <Users className="w-5 h-5 text-primary-400" />,
      subtitle: '34.5% share of voice',
    },
  ]

  return (
    <div className="grid grid-cols-6 gap-4">
      {kpis.map((kpi) => (
        <KPICard key={kpi.title} {...kpi} />
      ))}
    </div>
  )
}
