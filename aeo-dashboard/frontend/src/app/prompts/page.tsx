'use client'

import { useState } from 'react'

import { AppShell } from '@/components/ui/AppShell'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { DashboardHeader } from '@/components/ui/DashboardHeader'
import { Modal } from '@/components/ui/Modal'
import { PageHeader } from '@/components/ui/PageHeader'
import { Table, type Column } from '@/components/ui/Table'
import { useCheckVisibility, useCreatePrompt, useImportFromGSC, usePrompts } from '@/hooks/usePrompts'
import { useClientStore } from '@/stores/clientStore'

type Prompt = {
  id: number
  text: string
  source: string
  intent_type?: string | null
  is_branded: boolean
  gsc_impressions?: number | null
  gsc_avg_position?: number | null
  is_visible?: boolean | null
  visibility_score?: number | null
  last_checked_at?: string | null
}

export default function PromptsPage() {
  const { activeClientId } = useClientStore()
  const { data, isLoading } = usePrompts(activeClientId)
  const create = useCreatePrompt(activeClientId)
  const check = useCheckVisibility()
  const gsc = useImportFromGSC(activeClientId)

  const [addOpen, setAddOpen] = useState(false)
  const [text, setText] = useState('')
  const [importOpen, setImportOpen] = useState(false)
  const [minImpressions, setMinImpressions] = useState(1000)

  const rows = data?.items ?? []

  const columns: Column<Prompt>[] = [
    {
      key: 'text',
      header: 'Prompt',
      render: (row) => (
        <div>
          <p className="text-sm font-medium text-white">{row.text}</p>
          {row.intent_type && (
            <p className="text-xs text-dark-400 mt-0.5">{row.intent_type}</p>
          )}
        </div>
      ),
    },
    {
      key: 'source',
      header: 'Source',
      render: (row) => <Badge tone="neutral">{row.source}</Badge>,
    },
    {
      key: 'visible',
      header: 'Visible',
      render: (row) => (
        <Badge tone={row.is_visible ? 'success' : 'warning'}>
          {row.is_visible ? 'Yes' : 'No'}
        </Badge>
      ),
    },
    {
      key: 'score',
      header: 'Score',
      align: 'right',
      render: (row) => (row.visibility_score ?? 0).toFixed(1),
    },
    {
      key: 'gsc',
      header: 'GSC imp.',
      align: 'right',
      render: (row) => row.gsc_impressions?.toLocaleString() ?? '—',
    },
    {
      key: 'actions',
      header: '',
      align: 'right',
      render: (row) => (
        <Button
          size="sm"
          variant="secondary"
          isLoading={check.isPending}
          onClick={(e) => {
            e.stopPropagation()
            check.mutate({ promptId: row.id, checkCount: 2 })
          }}
        >
          Check now
        </Button>
      ),
    },
  ]

  return (
    <AppShell>
      <DashboardHeader title="Prompts" description="Conversational prompts you want to be cited for" />
      <PageHeader
        title="All prompts"
        actions={
          <>
            <Button variant="secondary" onClick={() => setImportOpen(true)}>
              Import from GSC
            </Button>
            <Button onClick={() => setAddOpen(true)}>Add prompt</Button>
          </>
        }
      />
      <Table
        columns={columns}
        rows={rows}
        isLoading={isLoading}
        emptyTitle="No prompts yet"
        emptyDescription="Add prompts manually or import them from Google Search Console."
        rowKey={(row) => row.id}
      />

      <Modal
        open={addOpen}
        onClose={() => setAddOpen(false)}
        title="Add prompt"
        footer={
          <>
            <Button variant="ghost" onClick={() => setAddOpen(false)}>
              Cancel
            </Button>
            <Button
              isLoading={create.isPending}
              onClick={() =>
                create.mutateAsync(text).then(() => {
                  setText('')
                  setAddOpen(false)
                })
              }
              disabled={text.trim().length < 3}
            >
              Add
            </Button>
          </>
        }
      >
        <textarea
          className="input h-28"
          placeholder="e.g. What are the best project management tools for startups?"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
      </Modal>

      <Modal
        open={importOpen}
        onClose={() => setImportOpen(false)}
        title="Import from Google Search Console"
        description="We'll convert your GSC queries into conversational prompts."
        footer={
          <>
            <Button variant="ghost" onClick={() => setImportOpen(false)}>
              Cancel
            </Button>
            <Button
              isLoading={gsc.isPending}
              onClick={() =>
                gsc
                  .mutateAsync({
                    min_impressions: minImpressions,
                    min_clicks: 10,
                    max_position: 50,
                    days_back: 90,
                  })
                  .then(() => setImportOpen(false))
              }
            >
              Run import
            </Button>
          </>
        }
      >
        <div className="space-y-3">
          <div>
            <label className="text-sm text-dark-300">Min impressions</label>
            <input
              type="number"
              className="input mt-1"
              value={minImpressions}
              onChange={(e) => setMinImpressions(Number(e.target.value))}
            />
          </div>
          <p className="text-xs text-dark-500">
            Runs against mock GSC data when no credentials are configured.
          </p>
        </div>
      </Modal>
    </AppShell>
  )
}
