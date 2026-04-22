'use client'

import { clsx } from 'clsx'
import { useState } from 'react'

import { AppShell } from '@/components/ui/AppShell'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { DashboardHeader } from '@/components/ui/DashboardHeader'
import { Modal } from '@/components/ui/Modal'
import { PageHeader } from '@/components/ui/PageHeader'
import { Table, type Column } from '@/components/ui/Table'
import { FreshnessOverview } from '@/components/modules/FreshnessOverview'
import { useAddContent, useAnalyzeContent, useContent, useFreshnessSummary } from '@/hooks/useContent'
import { useClientStore } from '@/stores/clientStore'

const gradeTone: Record<string, 'success' | 'info' | 'warning' | 'danger' | 'neutral'> = {
  A: 'success',
  B: 'info',
  C: 'warning',
  D: 'warning',
  F: 'danger',
}

type Content = {
  id: number
  url: string
  title?: string | null
  word_count?: number | null
  has_schema_markup: boolean
  freshness_score?: number | null
  freshness_grade?: string | null
  days_since_update?: number | null
}

export default function ContentPage() {
  const { activeClientId } = useClientStore()
  const { data, isLoading } = useContent(activeClientId)
  const { data: summary, isLoading: summaryLoading } = useFreshnessSummary(activeClientId)
  const add = useAddContent(activeClientId)
  const analyze = useAnalyzeContent(activeClientId)

  const [open, setOpen] = useState(false)
  const [url, setUrl] = useState('')

  const columns: Column<Content>[] = [
    {
      key: 'url',
      header: 'URL',
      render: (row) => (
        <div>
          <p className="text-sm font-medium text-white truncate max-w-xs">{row.title ?? row.url}</p>
          <p className="text-xs text-dark-500 truncate max-w-xs">{row.url}</p>
        </div>
      ),
    },
    {
      key: 'grade',
      header: 'Grade',
      render: (row) => (
        <Badge tone={gradeTone[row.freshness_grade ?? 'F'] ?? 'neutral'}>
          {row.freshness_grade ?? 'N/A'}
        </Badge>
      ),
    },
    {
      key: 'score',
      header: 'Score',
      align: 'right',
      render: (row) => (row.freshness_score ?? 0).toFixed(0),
    },
    {
      key: 'age',
      header: 'Age (days)',
      align: 'right',
      render: (row) => row.days_since_update ?? '—',
    },
    {
      key: 'schema',
      header: 'Schema',
      render: (row) => (
        <Badge tone={row.has_schema_markup ? 'success' : 'warning'}>
          {row.has_schema_markup ? 'yes' : 'missing'}
        </Badge>
      ),
    },
    {
      key: 'words',
      header: 'Words',
      align: 'right',
      render: (row) => row.word_count?.toLocaleString() ?? '—',
    },
    {
      key: 'actions',
      header: '',
      align: 'right',
      render: (row) => (
        <Button
          size="sm"
          variant="secondary"
          isLoading={analyze.isPending}
          onClick={(e) => {
            e.stopPropagation()
            analyze.mutate(row.id)
          }}
        >
          Re-analyze
        </Button>
      ),
    },
  ]

  return (
    <AppShell>
      <DashboardHeader title="Content" description="Track freshness and AI-optimization of your pages" />
      <PageHeader
        title={`${data?.length ?? 0} pages tracked`}
        actions={<Button onClick={() => setOpen(true)}>Add URL</Button>}
      />
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Table
            columns={columns}
            rows={data}
            isLoading={isLoading}
            emptyTitle="No tracked content"
            emptyDescription="Add a URL to start tracking freshness and schema coverage."
            rowKey={(row) => row.id}
          />
        </div>
        <div>
          <FreshnessOverview data={summary} isLoading={summaryLoading} />
        </div>
      </div>

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title="Add tracked URL"
        footer={
          <>
            <Button variant="ghost" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button
              isLoading={add.isPending}
              onClick={() =>
                add.mutateAsync(url).then(() => {
                  setUrl('')
                  setOpen(false)
                })
              }
              disabled={!url.startsWith('http')}
            >
              Add
            </Button>
          </>
        }
      >
        <input
          className="input"
          placeholder="https://example.com/page"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
      </Modal>
    </AppShell>
  )
}
