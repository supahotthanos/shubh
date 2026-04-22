'use client'

import { format, parseISO } from 'date-fns'
import { useState } from 'react'

import { AppShell } from '@/components/ui/AppShell'
import { Badge } from '@/components/ui/Badge'
import { DashboardHeader } from '@/components/ui/DashboardHeader'
import { FilterChips } from '@/components/ui/FilterBar'
import { PageHeader } from '@/components/ui/PageHeader'
import { Table, type Column } from '@/components/ui/Table'
import { useCitations, useCitationPlatformStats } from '@/hooks/useCitations'
import { useClientStore } from '@/stores/clientStore'

type Citation = {
  id: number
  platform_id: number
  prompt_id: number
  mention_type: 'linked' | 'unlinked' | 'brand_mention'
  position?: number | null
  cited_url?: string | null
  context_snippet?: string | null
  is_currently_visible: boolean
  last_seen_at?: string | null
  created_at: string
}

export default function CitationsPage() {
  const { activeClientId } = useClientStore()
  const [platform, setPlatform] = useState<string | null>(null)
  const [mention, setMention] = useState<string | null>(null)
  const params: Record<string, any> = { limit: 200 }
  if (platform) params.platform = platform
  if (mention) params.mention_type = mention

  const { data: citations, isLoading } = useCitations(activeClientId, params)
  const { data: platformStats } = useCitationPlatformStats(activeClientId)

  const platformOptions =
    (platformStats ?? []).map((p: any) => ({
      value: p.platform_slug,
      label: p.platform_name,
      count: p.total_citations,
    })) ?? []

  const columns: Column<Citation>[] = [
    {
      key: 'platform',
      header: 'Platform',
      render: (row) => {
        const label = platformStats?.find((p: any) => p.platform_slug === String(row.platform_id))?.platform_name
        return <Badge tone="primary">{label ?? `#${row.platform_id}`}</Badge>
      },
    },
    { key: 'prompt', header: 'Prompt', render: (row) => <span className="text-dark-300">#{row.prompt_id}</span> },
    {
      key: 'mention',
      header: 'Mention',
      render: (row) => {
        const tone =
          row.mention_type === 'linked' ? 'success' : row.mention_type === 'unlinked' ? 'info' : 'neutral'
        return <Badge tone={tone as any}>{row.mention_type.replace('_', ' ')}</Badge>
      },
    },
    {
      key: 'position',
      header: 'Position',
      align: 'right',
      render: (row) => (row.position ? `#${row.position}` : '—'),
    },
    {
      key: 'visible',
      header: 'Live',
      render: (row) => (
        <Badge tone={row.is_currently_visible ? 'success' : 'neutral'}>
          {row.is_currently_visible ? 'Yes' : 'No'}
        </Badge>
      ),
    },
    {
      key: 'snippet',
      header: 'Context',
      className: 'max-w-lg',
      render: (row) => (
        <span className="text-dark-400 text-xs line-clamp-2">
          {row.context_snippet ?? row.cited_url ?? '—'}
        </span>
      ),
    },
    {
      key: 'seen',
      header: 'Last seen',
      align: 'right',
      render: (row) =>
        row.last_seen_at ? format(parseISO(row.last_seen_at), 'MMM d') : '—',
    },
  ]

  return (
    <AppShell>
      <DashboardHeader
        title="Citations"
        description="Every mention of your brand across AI platforms"
      />
      <PageHeader
        title="All citations"
        filters={
          <div className="flex flex-wrap gap-4">
            <FilterChips options={platformOptions} value={platform} onChange={setPlatform} />
            <FilterChips
              options={[
                { value: 'linked', label: 'Linked' },
                { value: 'unlinked', label: 'Unlinked' },
                { value: 'brand_mention', label: 'Brand mention' },
              ]}
              value={mention}
              onChange={setMention}
            />
          </div>
        }
      />
      <Table
        columns={columns}
        rows={citations}
        isLoading={isLoading}
        emptyTitle="No citations yet"
        emptyDescription="Run a visibility check on a prompt to populate citations."
        rowKey={(row) => row.id}
      />
    </AppShell>
  )
}
