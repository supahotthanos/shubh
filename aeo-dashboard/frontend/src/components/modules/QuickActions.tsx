'use client'

import { RefreshCw, Code, Target, ArrowRight } from 'lucide-react'
import { clsx } from 'clsx'

interface QuickAction {
  id: string
  title: string
  description: string
  icon: React.ReactNode
  priority: number
  impact: 'high' | 'medium' | 'low'
  actionType: string
}

const actions: QuickAction[] = [
  {
    id: '1',
    title: 'Refresh Outdated Content',
    description: '4 pages need content updates to maintain freshness scores',
    icon: <RefreshCw className="w-5 h-5" />,
    priority: 1,
    impact: 'high',
    actionType: 'content_refresh',
  },
  {
    id: '2',
    title: 'Add Missing Schema Markup',
    description: '3 high-traffic pages missing structured data',
    icon: <Code className="w-5 h-5" />,
    priority: 2,
    impact: 'medium',
    actionType: 'schema_optimization',
  },
  {
    id: '3',
    title: 'Target New Keywords',
    description: '12 high-potential prompts identified from GSC data',
    icon: <Target className="w-5 h-5" />,
    priority: 3,
    impact: 'high',
    actionType: 'keyword_expansion',
  },
]

const impactColors = {
  high: 'text-green-400 bg-green-400/10',
  medium: 'text-yellow-400 bg-yellow-400/10',
  low: 'text-dark-400 bg-dark-700',
}

export function QuickActions() {
  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h2 className="card-title">Quick Actions</h2>
          <p className="text-sm text-dark-400 mt-1">
            Prioritized tasks based on your data
          </p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mt-4">
        {actions.map((action) => (
          <div
            key={action.id}
            className="p-4 bg-dark-800 rounded-lg border border-dark-700 hover:border-primary-500/50 transition-colors cursor-pointer group"
          >
            <div className="flex items-start justify-between">
              <div className={clsx('p-2 rounded-lg', impactColors[action.impact])}>
                {action.icon}
              </div>
              <span className={clsx('badge text-xs', impactColors[action.impact])}>
                {action.impact} impact
              </span>
            </div>

            <h3 className="mt-4 text-sm font-semibold text-white group-hover:text-primary-400 transition-colors">
              {action.title}
            </h3>
            <p className="mt-1 text-xs text-dark-400">
              {action.description}
            </p>

            <button className="mt-4 flex items-center gap-2 text-xs text-primary-400 hover:text-primary-300 transition-colors">
              Take Action
              <ArrowRight className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
