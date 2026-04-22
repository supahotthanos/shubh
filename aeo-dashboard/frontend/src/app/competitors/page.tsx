'use client'

import { useState } from 'react'

import { AppShell } from '@/components/ui/AppShell'
import { Badge } from '@/components/ui/Badge'
import { BarChart } from '@/components/charts/BarChart'
import { DonutChart } from '@/components/charts/DonutChart'
import { Button } from '@/components/ui/Button'
import { DashboardHeader } from '@/components/ui/DashboardHeader'
import { Modal } from '@/components/ui/Modal'
import { PageHeader } from '@/components/ui/PageHeader'
import { Table, type Column } from '@/components/ui/Table'
import {
  useAddCompetitor,
  useAnalyzeCompetitor,
  useCitationOverlap,
  useCompetitorComparison,
  useCompetitors,
} from '@/hooks/useCompetitors'
import { useClientStore } from '@/stores/clientStore'

type Competitor = {
  id: number
  name: string
  domain: string
  total_citations: number
  citation_share?: number | null
  avg_position?: number | null
  domain_rating?: number | null
  harmonic_centrality_rank?: number | null
}

export default function CompetitorsPage() {
  const { activeClientId } = useClientStore()
  const { data, isLoading } = useCompetitors(activeClientId)
  const { data: comparison } = useCompetitorComparison(activeClientId)
  const { data: overlap } = useCitationOverlap(activeClientId)
  const add = useAddCompetitor(activeClientId)
  const analyze = useAnalyzeCompetitor(activeClientId)

  const [open, setOpen] = useState(false)
  const [name, setName] = useState('')
  const [domain, setDomain] = useState('')

  const donutData = (comparison?.competitors ?? []).map((c: any) => ({
    name: c.name,
    value: c.total_citations,
  }))
  const barData = (comparison?.competitors ?? []).map((c: any) => ({
    name: c.name,
    citations: c.total_citations,
  }))

  const columns: Column<Competitor>[] = [
    { key: 'name', header: 'Competitor', render: (c) => <span className="text-white">{c.name}</span> },
    { key: 'domain', header: 'Domain', render: (c) => <span className="text-dark-400 text-xs">{c.domain}</span> },
    { key: 'cites', header: 'Citations', align: 'right', render: (c) => c.total_citations },
    {
      key: 'share',
      header: 'Share',
      align: 'right',
      render: (c) => (c.citation_share ?? 0).toFixed(1) + '%',
    },
    {
      key: 'dr',
      header: 'DR',
      align: 'right',
      render: (c) => c.domain_rating?.toFixed(0) ?? '—',
    },
    {
      key: 'hc',
      header: 'HC rank',
      align: 'right',
      render: (c) => c.harmonic_centrality_rank?.toLocaleString() ?? '—',
    },
    {
      key: 'actions',
      header: '',
      align: 'right',
      render: (c) => (
        <Button
          size="sm"
          variant="ghost"
          isLoading={analyze.isPending}
          onClick={(e) => {
            e.stopPropagation()
            analyze.mutate(c.id)
          }}
        >
          Analyze
        </Button>
      ),
    },
  ]

  return (
    <AppShell>
      <DashboardHeader title="Competitors" description="Share of voice, authority, and citation overlap" />
      <PageHeader
        title={`${data?.length ?? 0} competitors tracked`}
        actions={<Button onClick={() => setOpen(true)}>Add competitor</Button>}
      />

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="card">
          <h2 className="card-title">Share of voice</h2>
          <div className="mt-4">
            <DonutChart data={donutData} />
          </div>
        </div>
        <div className="card">
          <h2 className="card-title">Citations by competitor</h2>
          <div className="mt-4">
            <BarChart data={barData} xKey="name" yKey="citations" />
          </div>
        </div>
        <div className="card">
          <h2 className="card-title">Citation overlap</h2>
          <div className="mt-3 space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-dark-400">Overlap prompts</span>
              <span className="text-white">{overlap?.overlap_count ?? 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-dark-400">Competitor-only</span>
              <span className="text-white">{overlap?.competitor_only_count ?? 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-dark-400">Total competitor citations</span>
              <span className="text-white">{overlap?.total_competitor_citations ?? 0}</span>
            </div>
          </div>
        </div>
      </div>

      <Table
        columns={columns}
        rows={data}
        isLoading={isLoading}
        emptyTitle="No competitors tracked"
        rowKey={(c) => c.id}
      />

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title="Add competitor"
        footer={
          <>
            <Button variant="ghost" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button
              isLoading={add.isPending}
              onClick={() =>
                add
                  .mutateAsync({ name, domain })
                  .then(() => {
                    setName('')
                    setDomain('')
                    setOpen(false)
                  })
              }
              disabled={!name || !domain}
            >
              Add
            </Button>
          </>
        }
      >
        <div className="space-y-3">
          <div>
            <label className="text-sm text-dark-300">Name</label>
            <input className="input mt-1" value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div>
            <label className="text-sm text-dark-300">Domain</label>
            <input
              className="input mt-1"
              placeholder="example.com"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
            />
          </div>
        </div>
      </Modal>
    </AppShell>
  )
}
