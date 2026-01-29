'use client'

import { Target, Check, AlertTriangle } from 'lucide-react'

interface RRFEntry {
  keyword: string
  score: number
  meetsThreshold: boolean
  appearances: number
  avgRank: number
}

const rrfData: RRFEntry[] = [
  { keyword: 'best crm software', score: 0.028, meetsThreshold: true, appearances: 3, avgRank: 35 },
  { keyword: 'project management tools', score: 0.024, meetsThreshold: true, appearances: 2, avgRank: 28 },
  { keyword: 'email marketing platform', score: 0.018, meetsThreshold: false, appearances: 2, avgRank: 52 },
  { keyword: 'seo automation tool', score: 0.015, meetsThreshold: false, appearances: 1, avgRank: 45 },
]

const THRESHOLD = 0.020

export function RRFScoreCard() {
  const meetingThreshold = rrfData.filter(k => k.meetsThreshold).length
  const total = rrfData.length

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h2 className="card-title">RRF Visibility Score</h2>
          <p className="text-sm text-dark-400 mt-1">
            k=60, threshold=0.020
          </p>
        </div>
        <div className="badge badge-info">
          {meetingThreshold}/{total} at threshold
        </div>
      </div>

      {/* Quick Reference */}
      <div className="mt-4 p-3 bg-dark-800 rounded-lg">
        <p className="text-xs text-dark-400 mb-2">Quick Reference</p>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="flex justify-between">
            <span className="text-dark-500">2x at ≤40:</span>
            <span className="text-green-400">0.020 ✓</span>
          </div>
          <div className="flex justify-between">
            <span className="text-dark-500">3x at ≤90:</span>
            <span className="text-green-400">0.020 ✓</span>
          </div>
          <div className="flex justify-between">
            <span className="text-dark-500">4x at ≤140:</span>
            <span className="text-green-400">0.020 ✓</span>
          </div>
          <div className="flex justify-between">
            <span className="text-dark-500">1x #1 + 1x ≤80:</span>
            <span className="text-green-400">0.024 ✓</span>
          </div>
        </div>
      </div>

      {/* Keywords List */}
      <div className="mt-4 space-y-3">
        {rrfData.map((entry) => (
          <div
            key={entry.keyword}
            className="flex items-center justify-between p-3 bg-dark-800 rounded-lg"
          >
            <div className="flex items-center gap-3">
              {entry.meetsThreshold ? (
                <Check className="w-4 h-4 text-green-400" />
              ) : (
                <AlertTriangle className="w-4 h-4 text-yellow-400" />
              )}
              <div>
                <p className="text-sm font-medium text-white">{entry.keyword}</p>
                <p className="text-xs text-dark-500">
                  {entry.appearances}x appearances, avg rank #{entry.avgRank}
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className={`text-sm font-mono ${entry.meetsThreshold ? 'text-green-400' : 'text-yellow-400'}`}>
                {entry.score.toFixed(4)}
              </p>
              {!entry.meetsThreshold && (
                <p className="text-xs text-dark-500">
                  need +{(THRESHOLD - entry.score).toFixed(4)}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>

      <button className="mt-4 w-full btn btn-secondary text-sm">
        View All Keywords
      </button>
    </div>
  )
}
