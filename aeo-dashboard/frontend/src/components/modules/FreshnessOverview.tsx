'use client'

import { clsx } from 'clsx'
import Link from 'next/link'

import { EmptyState } from '@/components/ui/EmptyState'
import { Skeleton } from '@/components/ui/Skeleton'

const gradeBg: Record<string, string> = {
  A: 'bg-green-500',
  B: 'bg-blue-500',
  C: 'bg-yellow-500',
  D: 'bg-orange-500',
  F: 'bg-red-500',
}

const gradeText: Record<string, string> = {
  A: 'text-green-400',
  B: 'text-blue-400',
  C: 'text-yellow-400',
  D: 'text-orange-400',
  F: 'text-red-400',
}

export function FreshnessOverview({ data, isLoading }: { data?: any; isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Content freshness</h2>
        </div>
        <Skeleton className="h-32 w-full" />
      </div>
    )
  }

  const dist = data?.grade_distribution ?? { A: 0, B: 0, C: 0, D: 0, F: 0 }
  const total = Object.values(dist).reduce((a: number, b: any) => a + Number(b || 0), 0) as number

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h2 className="card-title">Content freshness</h2>
          <p className="text-sm text-dark-400 mt-1">{total} pages tracked</p>
        </div>
        <div className={clsx('text-2xl font-bold', gradeText[data?.overall_grade ?? 'N/A'] ?? 'text-dark-400')}>
          {data?.overall_grade ?? '—'}
        </div>
      </div>

      {total === 0 ? (
        <EmptyState title="Nothing tracked" description="Add URLs on the Content page to start tracking freshness." />
      ) : (
        <>
          <div className="flex h-3 rounded-full overflow-hidden mt-4">
            {['A', 'B', 'C', 'D', 'F'].map((grade) => (
              <div
                key={grade}
                className={clsx('h-full', gradeBg[grade])}
                style={{ width: `${((dist[grade] || 0) / total) * 100}%` }}
              />
            ))}
          </div>
          <div className="flex justify-between mt-2 text-xs text-dark-400">
            {['A', 'B', 'C', 'D', 'F'].map((g) => (
              <span key={g}>{g}: {dist[g] || 0}</span>
            ))}
          </div>

          {data?.needs_refresh?.length > 0 && (
            <div className="mt-4 space-y-2">
              <p className="text-xs text-dark-400">Needs refresh</p>
              {data.needs_refresh.slice(0, 3).map((item: any, idx: number) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-2 bg-dark-800 rounded-lg"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <div
                      className={clsx(
                        'w-6 h-6 rounded flex items-center justify-center text-xs font-bold',
                        gradeText[item.grade] ?? 'text-dark-400',
                      )}
                    >
                      {item.grade}
                    </div>
                    <p className="text-xs text-white truncate max-w-[170px]">{item.title || item.url}</p>
                  </div>
                  <span className="text-xs text-red-400">-{item.position_loss}</span>
                </div>
              ))}
            </div>
          )}
          <Link href="/content" className="mt-4 block">
            <button className="w-full btn btn-secondary text-sm">View all content</button>
          </Link>
        </>
      )}
    </div>
  )
}
