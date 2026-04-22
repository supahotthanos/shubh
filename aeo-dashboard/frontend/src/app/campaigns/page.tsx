'use client'

import { useState } from 'react'

import { AppShell } from '@/components/ui/AppShell'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { DashboardHeader } from '@/components/ui/DashboardHeader'
import { Modal } from '@/components/ui/Modal'
import { PageHeader } from '@/components/ui/PageHeader'
import { Table, type Column } from '@/components/ui/Table'
import { useCampaigns, useCampaignSummary, useCreateCampaign } from '@/hooks/useCampaigns'
import { useClientStore } from '@/stores/clientStore'

const CAMPAIGN_TYPES = [
  'content_publish',
  'guest_post',
  'press_release',
  'research_report',
  'listicle',
  'thought_leadership',
  'community_engagement',
]

type Campaign = {
  id: number
  name: string
  campaign_type: string
  status: string
  target_citations?: number | null
  budget?: number | null
  spent: number
  start_date?: string | null
}

export default function CampaignsPage() {
  const { activeClientId } = useClientStore()
  const { data, isLoading } = useCampaigns(activeClientId)
  const { data: summary } = useCampaignSummary(activeClientId)
  const create = useCreateCampaign(activeClientId)
  const [open, setOpen] = useState(false)
  const [name, setName] = useState('')
  const [type, setType] = useState(CAMPAIGN_TYPES[0])

  const columns: Column<Campaign>[] = [
    { key: 'name', header: 'Campaign', render: (c) => <span className="text-white font-medium">{c.name}</span> },
    {
      key: 'type',
      header: 'Type',
      render: (c) => <Badge tone="primary">{c.campaign_type.replace('_', ' ')}</Badge>,
    },
    {
      key: 'status',
      header: 'Status',
      render: (c) => (
        <Badge tone={c.status === 'active' ? 'success' : c.status === 'paused' ? 'warning' : 'neutral'}>
          {c.status}
        </Badge>
      ),
    },
    {
      key: 'target',
      header: 'Target citations',
      align: 'right',
      render: (c) => c.target_citations ?? '—',
    },
    {
      key: 'budget',
      header: 'Budget',
      align: 'right',
      render: (c) =>
        c.budget ? `$${c.spent?.toLocaleString() ?? 0} / $${c.budget.toLocaleString()}` : '—',
    },
  ]

  return (
    <AppShell>
      <DashboardHeader title="Campaigns" description="Content marketing efforts by type and status" />
      <PageHeader
        title={`${data?.length ?? 0} campaigns`}
        actions={<Button onClick={() => setOpen(true)}>New campaign</Button>}
      />

      {summary && summary.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
          {summary.map((s: any) => (
            <div key={s.campaign_type} className="card">
              <p className="text-xs text-dark-400">{s.campaign_type.replace('_', ' ')}</p>
              <p className="stat-value mt-1">{s.total_campaigns}</p>
              <p className="text-xs text-dark-500 mt-1">
                {s.active_campaigns} active · {s.total_assets} assets
              </p>
            </div>
          ))}
        </div>
      )}

      <Table
        columns={columns}
        rows={data}
        isLoading={isLoading}
        emptyTitle="No campaigns yet"
        emptyDescription="Create a campaign to track listicles, PR, guest posts, and research reports."
        rowKey={(c) => c.id}
      />

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title="New campaign"
        footer={
          <>
            <Button variant="ghost" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button
              isLoading={create.isPending}
              onClick={() =>
                create
                  .mutateAsync({ name, campaign_type: type })
                  .then(() => {
                    setName('')
                    setOpen(false)
                  })
              }
              disabled={name.length < 2}
            >
              Create
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
            <label className="text-sm text-dark-300">Type</label>
            <select className="input mt-1" value={type} onChange={(e) => setType(e.target.value)}>
              {CAMPAIGN_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t.replace('_', ' ')}
                </option>
              ))}
            </select>
          </div>
        </div>
      </Modal>
    </AppShell>
  )
}
