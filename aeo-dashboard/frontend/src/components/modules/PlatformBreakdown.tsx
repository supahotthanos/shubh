'use client'

import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { clsx } from 'clsx'

interface Platform {
  name: string
  slug: string
  citations: number
  avgPosition: number
  stability: number
  trend: 'up' | 'down' | 'stable'
  trendValue: number
}

const platforms: Platform[] = [
  { name: 'ChatGPT', slug: 'chatgpt', citations: 58, avgPosition: 1.8, stability: 82, trend: 'up', trendValue: 12.5 },
  { name: 'Perplexity', slug: 'perplexity', citations: 42, avgPosition: 2.1, stability: 76, trend: 'stable', trendValue: 2.1 },
  { name: 'Claude', slug: 'claude', citations: 28, avgPosition: 1.5, stability: 88, trend: 'up', trendValue: 18.2 },
  { name: 'Google AI', slug: 'google_ai', citations: 14, avgPosition: 2.4, stability: 65, trend: 'down', trendValue: -8.3 },
]

export function PlatformBreakdown() {
  const totalCitations = platforms.reduce((acc, p) => acc + p.citations, 0)

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">Platform Breakdown</h2>
        <span className="text-sm text-dark-400">{totalCitations} total</span>
      </div>

      <div className="space-y-4">
        {platforms.map((platform) => {
          const percentage = (platform.citations / totalCitations) * 100
          const TrendIcon = platform.trend === 'up' ? TrendingUp : platform.trend === 'down' ? TrendingDown : Minus

          return (
            <div key={platform.slug} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-dark-800 rounded-lg flex items-center justify-center text-xs font-bold text-primary-400">
                    {platform.name.charAt(0)}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white">{platform.name}</p>
                    <p className="text-xs text-dark-500">
                      Avg pos: {platform.avgPosition.toFixed(1)} | Stability: {platform.stability}%
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold text-white">{platform.citations}</p>
                  <div className={clsx(
                    'flex items-center gap-1 text-xs',
                    platform.trend === 'up' && 'text-green-400',
                    platform.trend === 'down' && 'text-red-400',
                    platform.trend === 'stable' && 'text-dark-400'
                  )}>
                    <TrendIcon className="w-3 h-3" />
                    <span>{platform.trendValue > 0 ? '+' : ''}{platform.trendValue}%</span>
                  </div>
                </div>
              </div>

              {/* Progress bar */}
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
    </div>
  )
}
