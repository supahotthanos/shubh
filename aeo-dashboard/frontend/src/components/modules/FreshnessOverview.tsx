'use client'

import { FileText, AlertCircle, Clock } from 'lucide-react'
import { clsx } from 'clsx'

interface FreshnessItem {
  url: string
  title: string
  grade: 'A' | 'B' | 'C' | 'D' | 'F'
  daysOld: number
  positionLoss: number
  priority: 'critical' | 'high' | 'medium' | 'low'
}

const freshnessData: FreshnessItem[] = [
  { url: '/best-seo-tools', title: 'Best SEO Tools 2024', grade: 'F', daysOld: 420, positionLoss: 65, priority: 'critical' },
  { url: '/crm-comparison', title: 'CRM Software Comparison', grade: 'D', daysOld: 280, positionLoss: 35, priority: 'high' },
  { url: '/email-marketing', title: 'Email Marketing Guide', grade: 'C', daysOld: 185, positionLoss: 15, priority: 'medium' },
  { url: '/project-mgmt', title: 'Project Management Tips', grade: 'B', daysOld: 95, positionLoss: 5, priority: 'low' },
]

const gradeColors = {
  A: 'text-green-400 bg-green-400/10',
  B: 'text-blue-400 bg-blue-400/10',
  C: 'text-yellow-400 bg-yellow-400/10',
  D: 'text-orange-400 bg-orange-400/10',
  F: 'text-red-400 bg-red-400/10',
}

const priorityColors = {
  critical: 'badge-danger',
  high: 'badge-warning',
  medium: 'badge-info',
  low: 'badge-success',
}

export function FreshnessOverview() {
  const gradeDistribution = { A: 10, B: 15, C: 8, D: 3, F: 1 }
  const total = Object.values(gradeDistribution).reduce((a, b) => a + b, 0)

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h2 className="card-title">Content Freshness</h2>
          <p className="text-sm text-dark-400 mt-1">
            {total} pages tracked
          </p>
        </div>
        <div className="text-2xl font-bold text-blue-400">B</div>
      </div>

      {/* Grade Distribution Bar */}
      <div className="mt-4">
        <div className="flex h-3 rounded-full overflow-hidden">
          {Object.entries(gradeDistribution).map(([grade, count]) => (
            <div
              key={grade}
              className={clsx(
                'h-full',
                grade === 'A' && 'bg-green-500',
                grade === 'B' && 'bg-blue-500',
                grade === 'C' && 'bg-yellow-500',
                grade === 'D' && 'bg-orange-500',
                grade === 'F' && 'bg-red-500'
              )}
              style={{ width: `${(count / total) * 100}%` }}
            />
          ))}
        </div>
        <div className="flex justify-between mt-2 text-xs text-dark-400">
          {Object.entries(gradeDistribution).map(([grade, count]) => (
            <span key={grade}>{grade}: {count}</span>
          ))}
        </div>
      </div>

      {/* Model-Specific Targets */}
      <div className="mt-4 p-3 bg-dark-800 rounded-lg">
        <p className="text-xs text-dark-400 mb-2">Recommended Update Frequency</p>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="flex justify-between">
            <span className="text-dark-500">GPT-based:</span>
            <span className="text-white">6-12 months</span>
          </div>
          <div className="flex justify-between">
            <span className="text-dark-500">LLaMA-based:</span>
            <span className="text-white">3-6 months</span>
          </div>
        </div>
      </div>

      {/* Pages Needing Refresh */}
      <div className="mt-4 space-y-2">
        <p className="text-xs text-dark-400">Needs Refresh</p>
        {freshnessData.slice(0, 3).map((item) => (
          <div
            key={item.url}
            className="flex items-center justify-between p-2 bg-dark-800 rounded-lg"
          >
            <div className="flex items-center gap-2">
              <div className={clsx('w-6 h-6 rounded flex items-center justify-center text-xs font-bold', gradeColors[item.grade])}>
                {item.grade}
              </div>
              <div>
                <p className="text-xs font-medium text-white truncate max-w-[140px]">{item.title}</p>
                <p className="text-xs text-dark-500">{item.daysOld} days old</p>
              </div>
            </div>
            <span className={clsx('badge text-xs', priorityColors[item.priority])}>
              -{item.positionLoss} pos
            </span>
          </div>
        ))}
      </div>

      <button className="mt-4 w-full btn btn-secondary text-sm">
        View All Content
      </button>
    </div>
  )
}
