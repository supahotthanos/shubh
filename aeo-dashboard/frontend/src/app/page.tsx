'use client'

import { useState } from 'react'

import { AppShell } from '@/components/ui/AppShell'
import { DashboardHeader } from '@/components/ui/DashboardHeader'
import { FilterChips } from '@/components/ui/FilterBar'
import { CitationTrendChart } from '@/components/charts/CitationTrendChart'
import { AlertsPanel } from '@/components/modules/AlertsPanel'
import { FreshnessOverview } from '@/components/modules/FreshnessOverview'
import { KPICards } from '@/components/modules/KPICards'
import { PlatformBreakdown } from '@/components/modules/PlatformBreakdown'
import { QuickActions } from '@/components/modules/QuickActions'
import { RRFScoreCard } from '@/components/modules/RRFScoreCard'
import {
  useCitationTrend,
  useDashboardAlerts,
  useDashboardMetrics,
  usePlatformBreakdown,
  useQuickActions,
} from '@/hooks/useDashboard'
import { useFreshnessSummary } from '@/hooks/useContent'
import { useClientStore } from '@/stores/clientStore'

export default function DashboardPage() {
  const { activeClientId } = useClientStore()
  const [period, setPeriod] = useState<'7d' | '30d' | '60d' | '90d'>('30d')

  const { data: metrics, isLoading: metricsLoading } = useDashboardMetrics(activeClientId, period)
  const { data: platforms, isLoading: platformsLoading } = usePlatformBreakdown(activeClientId)
  const { data: trend, isLoading: trendLoading } = useCitationTrend(activeClientId, period)
  const { data: alerts, isLoading: alertsLoading } = useDashboardAlerts(activeClientId)
  const { data: quickActions, isLoading: qaLoading } = useQuickActions(activeClientId)
  const { data: freshness, isLoading: freshnessLoading } = useFreshnessSummary(activeClientId)

  return (
    <AppShell>
      <DashboardHeader
        title="Dashboard"
        description="Track your AI visibility across ChatGPT, Perplexity, Claude, Gemini, and more"
        right={
          <FilterChips
            options={[
              { value: '7d', label: '7d' },
              { value: '30d', label: '30d' },
              { value: '60d', label: '60d' },
              { value: '90d', label: '90d' },
            ]}
            value={period}
            onChange={(v) => setPeriod((v ?? '30d') as any)}
            allowClear={false}
          />
        }
      />

      <KPICards metrics={metrics} isLoading={metricsLoading} />

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        <div className="xl:col-span-8">
          <CitationTrendChart data={trend} isLoading={trendLoading} />
        </div>
        <div className="xl:col-span-4">
          <AlertsPanel data={alerts} isLoading={alertsLoading} />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <PlatformBreakdown platforms={platforms ?? []} isLoading={platformsLoading} />
        <RRFScoreCard clientId={activeClientId} />
        <FreshnessOverview data={freshness} isLoading={freshnessLoading} />
      </div>

      <QuickActions data={quickActions} isLoading={qaLoading} />
    </AppShell>
  )
}
