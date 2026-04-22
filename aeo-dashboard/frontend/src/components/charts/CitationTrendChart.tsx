'use client'

import { Skeleton } from '@/components/ui/Skeleton'
import { LineChart } from './LineChart'

interface Props {
  data?: { data_points?: { date: string; citations: number; stability: number }[] }
  isLoading?: boolean
}

export function CitationTrendChart({ data, isLoading }: Props) {
  const points = data?.data_points ?? []
  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h2 className="card-title">Citation trend</h2>
          <p className="text-sm text-dark-400 mt-1">Cumulative citations over the selected period</p>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-primary-500" /> Citations
          </div>
        </div>
      </div>
      <div className="mt-4">
        {isLoading ? (
          <Skeleton className="h-64 w-full" />
        ) : (
          <LineChart data={points} xKey="date" yKey="citations" label="Citations" height={260} />
        )}
      </div>
    </div>
  )
}
