'use client'

import { useState } from 'react'

import { AppShell } from '@/components/ui/AppShell'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { DashboardHeader } from '@/components/ui/DashboardHeader'
import { Modal } from '@/components/ui/Modal'
import { PageHeader } from '@/components/ui/PageHeader'
import { Table, type Column } from '@/components/ui/Table'
import {
  useAddKeyword,
  useKeywords,
  useRRFQuickReference,
  useRRFRecommendations,
  useRRFScores,
  useSimulateImprovement,
} from '@/hooks/useKeywords'
import { useClientStore } from '@/stores/clientStore'

type RRFRow = {
  id: number
  keyword_id: number
  keyword_text?: string
  raw_score: number
  meets_threshold: boolean
  total_appearances: number
  avg_rank: number
  best_rank: number
  worst_rank: number
  appearances_needed: number
  target_rank_each: number
}

export default function KeywordsPage() {
  const { activeClientId } = useClientStore()
  const { data: keywords, isLoading: keywordsLoading } = useKeywords(activeClientId)
  const { data: rrfScores, isLoading: rrfLoading } = useRRFScores(activeClientId)
  const { data: quickRef } = useRRFQuickReference()
  const { data: recs } = useRRFRecommendations(activeClientId)
  const add = useAddKeyword(activeClientId)
  const simulate = useSimulateImprovement()

  const [open, setOpen] = useState(false)
  const [text, setText] = useState('')
  const [simRank, setSimRank] = useState(40)

  const columns: Column<RRFRow>[] = [
    { key: 'keyword', header: 'Keyword', render: (r) => r.keyword_text ?? `#${r.keyword_id}` },
    {
      key: 'score',
      header: 'RRF',
      align: 'right',
      render: (r) => (
        <span className={r.meets_threshold ? 'text-green-400 font-mono' : 'text-yellow-400 font-mono'}>
          {r.raw_score.toFixed(4)}
        </span>
      ),
    },
    {
      key: 'threshold',
      header: 'Threshold',
      render: (r) => (
        <Badge tone={r.meets_threshold ? 'success' : 'warning'}>
          {r.meets_threshold ? 'met' : 'below'}
        </Badge>
      ),
    },
    { key: 'appearances', header: '# appearances', align: 'right', render: (r) => r.total_appearances },
    { key: 'avg', header: 'Avg rank', align: 'right', render: (r) => Math.round(r.avg_rank ?? 0) },
    {
      key: 'needed',
      header: 'Needed',
      align: 'right',
      render: (r) =>
        r.meets_threshold
          ? '—'
          : `${r.appearances_needed} @ ≤${r.target_rank_each}`,
    },
    {
      key: 'sim',
      header: '',
      align: 'right',
      render: (r) => (
        <Button
          size="sm"
          variant="ghost"
          onClick={(e) => {
            e.stopPropagation()
            simulate.mutate({ keywordId: r.keyword_id, newRank: simRank })
          }}
        >
          Simulate +1 @ {simRank}
        </Button>
      ),
    },
  ]

  return (
    <AppShell>
      <DashboardHeader
        title="Keywords & RRF"
        description="Reciprocal Rank Fusion scoring (k=60, threshold 0.0200)"
      />
      <PageHeader
        title={`${keywords?.length ?? 0} keywords tracked`}
        actions={<Button onClick={() => setOpen(true)}>Add keyword</Button>}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Table
            columns={columns}
            rows={rrfScores}
            isLoading={rrfLoading || keywordsLoading}
            emptyTitle="No RRF scores yet"
            emptyDescription="Calculate RRF for a keyword by submitting its sub-query rankings via POST /keywords/calculate-rrf."
            rowKey={(r) => r.id}
          />
        </div>
        <div className="space-y-4">
          <div className="card">
            <h2 className="card-title">Quick reference</h2>
            <p className="text-xs text-dark-400 mt-1">
              Combinations guaranteed to meet τ = 0.0200
            </p>
            <div className="mt-4 space-y-2 text-sm">
              {(quickRef ?? []).map((row: any) => (
                <div key={row.appearances} className="flex justify-between">
                  <span className="text-dark-400">
                    {row.appearances}× at ≤{row.max_rank_each}
                  </span>
                  <span className={row.meets_threshold ? 'text-green-400 font-mono' : 'text-dark-300 font-mono'}>
                    {row.guaranteed_score.toFixed(4)} {row.meets_threshold && '✓'}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <h2 className="card-title">Simulator</h2>
            <p className="text-xs text-dark-400 mt-1">
              Pick a new target rank — the simulate buttons in the table project each row's new RRF.
            </p>
            <input
              type="range"
              min={1}
              max={200}
              value={simRank}
              onChange={(e) => setSimRank(Number(e.target.value))}
              className="w-full mt-3"
            />
            <p className="text-sm text-dark-300 mt-1">
              Target rank: <span className="font-mono">{simRank}</span>
            </p>
            {simulate.data && (
              <p className="text-xs text-dark-400 mt-2">{simulate.data.message}</p>
            )}
          </div>

          <div className="card">
            <h2 className="card-title">Top recommendations</h2>
            <div className="mt-3 space-y-3">
              {(recs ?? []).slice(0, 5).map((rec: any, idx: number) => (
                <div key={idx} className="text-xs">
                  <p className="text-dark-200 font-medium">{rec.keyword}</p>
                  <p className="text-dark-500">{rec.recommendation}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title="Add keyword"
        footer={
          <>
            <Button variant="ghost" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button
              isLoading={add.isPending}
              onClick={() =>
                add.mutateAsync(text).then(() => {
                  setText('')
                  setOpen(false)
                })
              }
              disabled={text.length < 2}
            >
              Add
            </Button>
          </>
        }
      >
        <input
          className="input"
          placeholder="e.g. best crm software"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
      </Modal>
    </AppShell>
  )
}
