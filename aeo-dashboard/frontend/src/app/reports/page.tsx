'use client'

import { format, parseISO } from 'date-fns'
import { Download } from 'lucide-react'
import { useState } from 'react'

import { AppShell } from '@/components/ui/AppShell'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { DashboardHeader } from '@/components/ui/DashboardHeader'
import { Modal } from '@/components/ui/Modal'
import { PageHeader } from '@/components/ui/PageHeader'
import { Table, type Column } from '@/components/ui/Table'
import { useClientStore } from '@/stores/clientStore'
import { useDownloadReport, useGenerateReport, useReportSchedules, useReports } from '@/hooks/useReports'

type Report = {
  id: number
  title: string
  report_type: string
  period_start?: string | null
  period_end?: string | null
  generated_at?: string | null
  status: string
}

export default function ReportsPage() {
  const { activeClientId } = useClientStore()
  const { data, isLoading } = useReports(activeClientId)
  const { data: schedules } = useReportSchedules(activeClientId)
  const generate = useGenerateReport(activeClientId)
  const download = useDownloadReport()

  const [open, setOpen] = useState(false)
  const [reportType, setReportType] = useState<'weekly' | 'monthly' | 'quarterly'>('monthly')

  const columns: Column<Report>[] = [
    { key: 'title', header: 'Report', render: (r) => <span className="text-white">{r.title}</span> },
    {
      key: 'type',
      header: 'Type',
      render: (r) => <Badge tone="primary">{r.report_type}</Badge>,
    },
    {
      key: 'range',
      header: 'Range',
      render: (r) =>
        r.period_start && r.period_end
          ? `${format(parseISO(r.period_start), 'MMM d')} – ${format(parseISO(r.period_end), 'MMM d')}`
          : '—',
    },
    {
      key: 'gen',
      header: 'Generated',
      render: (r) =>
        r.generated_at ? format(parseISO(r.generated_at), 'MMM d, HH:mm') : '—',
    },
    {
      key: 'status',
      header: 'Status',
      render: (r) => <Badge tone={r.status === 'published' ? 'success' : 'neutral'}>{r.status}</Badge>,
    },
    {
      key: 'actions',
      header: '',
      align: 'right',
      render: (r) => (
        <div className="flex justify-end gap-2">
          <Button
            size="sm"
            variant="ghost"
            isLoading={download.isPending}
            onClick={(e) => {
              e.stopPropagation()
              download.mutate({ id: r.id, format: 'csv' })
            }}
          >
            <Download className="w-3 h-3" /> CSV
          </Button>
          <Button
            size="sm"
            variant="secondary"
            isLoading={download.isPending}
            onClick={(e) => {
              e.stopPropagation()
              download.mutate({ id: r.id, format: 'pdf' })
            }}
          >
            <Download className="w-3 h-3" /> PDF
          </Button>
        </div>
      ),
    },
  ]

  return (
    <AppShell>
      <DashboardHeader title="Reports" description="On-demand and scheduled AEO reports" />
      <PageHeader
        title={`${data?.length ?? 0} reports`}
        actions={<Button onClick={() => setOpen(true)}>Generate report</Button>}
      />

      <Table
        columns={columns}
        rows={data}
        isLoading={isLoading}
        emptyTitle="No reports yet"
        emptyDescription="Generate a weekly, monthly, or quarterly report to share with stakeholders."
        rowKey={(r) => r.id}
      />

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Schedules</h2>
        </div>
        {schedules && schedules.length > 0 ? (
          <div className="space-y-2">
            {schedules.map((s: any) => (
              <div
                key={s.id}
                className="flex items-center justify-between p-3 rounded-lg bg-dark-800"
              >
                <div>
                  <p className="text-sm text-white capitalize">{s.frequency}</p>
                  <p className="text-xs text-dark-500">
                    Recipients: {(s.recipients ?? []).join(', ') || '—'}
                  </p>
                </div>
                <Badge tone={s.is_active ? 'success' : 'neutral'}>
                  {s.is_active ? 'active' : 'paused'}
                </Badge>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-dark-400">No schedules configured yet.</p>
        )}
      </div>

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title="Generate report"
        footer={
          <>
            <Button variant="ghost" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button
              isLoading={generate.isPending}
              onClick={() =>
                generate.mutateAsync(reportType).then(() => setOpen(false))
              }
            >
              Generate
            </Button>
          </>
        }
      >
        <label className="text-sm text-dark-300">Report type</label>
        <select
          className="input mt-1"
          value={reportType}
          onChange={(e) => setReportType(e.target.value as any)}
        >
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
          <option value="quarterly">Quarterly</option>
        </select>
      </Modal>
    </AppShell>
  )
}
