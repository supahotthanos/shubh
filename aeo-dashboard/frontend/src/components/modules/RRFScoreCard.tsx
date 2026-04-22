'use client'

import { AlertTriangle, Check } from 'lucide-react'
import Link from 'next/link'

import { EmptyState } from '@/components/ui/EmptyState'
import { Skeleton } from '@/components/ui/Skeleton'
import { useRRFScores, useRRFQuickReference } from '@/hooks/useKeywords'

const THRESHOLD = 0.02

export function RRFScoreCard({ clientId }: { clientId: number | null }) {
  const { data, isLoading } = useRRFScores(clientId)
  const { data: quickRef } = useRRFQuickReference()

  const rows = (data ?? []).slice(0, 5)
  const meeting = rows.filter((r: any) => r.meets_threshold).length

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h2 className="card-title">RRF visibility</h2>
          <p className="text-sm text-dark-400 mt-1">k=60, threshold=0.020</p>
        </div>
        <div className="badge badge-info">
          {meeting}/{rows.length} at τ
        </div>
      </div>

      {quickRef && (
        <div className="mt-4 p-3 bg-dark-800 rounded-lg">
          <p className="text-xs text-dark-400 mb-2">Quick reference</p>
          <div className="grid grid-cols-2 gap-2 text-xs">
            {quickRef.slice(0, 4).map((row: any) => (
              <div key={row.appearances} className="flex justify-between">
                <span className="text-dark-500">
                  {row.appearances}× at ≤{row.max_rank_each}:
                </span>
                <span className={row.meets_threshold ? 'text-green-400' : 'text-dark-300'}>
                  {row.guaranteed_score.toFixed(4)} {row.meets_threshold && '✓'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mt-4 space-y-3">
        {isLoading ? (
          <>
            <Skeleton className="h-12 w-full" />
            <Skeleton className="h-12 w-full" />
          </>
        ) : rows.length === 0 ? (
          <EmptyState title="No RRF data" description="Add keywords and calculate RRF scores on the Keywords page." />
        ) : (
          rows.map((entry: any) => (
            <div
              key={entry.id}
              className="flex items-center justify-between p-3 bg-dark-800 rounded-lg"
            >
              <div className="flex items-center gap-3 min-w-0">
                {entry.meets_threshold ? (
                  <Check className="w-4 h-4 text-green-400 flex-shrink-0" />
                ) : (
                  <AlertTriangle className="w-4 h-4 text-yellow-400 flex-shrink-0" />
                )}
                <div className="min-w-0">
                  <p className="text-sm font-medium text-white truncate">
                    {entry.keyword_text ?? 'keyword'}
                  </p>
                  <p className="text-xs text-dark-500">
                    {entry.total_appearances}× appearances · avg rank #{Math.round(entry.avg_rank ?? 0)}
                  </p>
                </div>
              </div>
              <p
                className={`text-sm font-mono ${
                  entry.meets_threshold ? 'text-green-400' : 'text-yellow-400'
                }`}
              >
                {entry.raw_score?.toFixed(4)}
              </p>
            </div>
          ))
        )}
      </div>

      <Link href="/keywords" className="mt-4 block">
        <button className="w-full btn btn-secondary text-sm">View all keywords</button>
      </Link>
    </div>
  )
}
