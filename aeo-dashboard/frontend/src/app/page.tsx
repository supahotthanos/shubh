import { Sidebar } from '@/components/ui/Sidebar'
import { DashboardHeader } from '@/components/ui/DashboardHeader'
import { KPICards } from '@/components/modules/KPICards'
import { CitationTrendChart } from '@/components/charts/CitationTrendChart'
import { PlatformBreakdown } from '@/components/modules/PlatformBreakdown'
import { RRFScoreCard } from '@/components/modules/RRFScoreCard'
import { FreshnessOverview } from '@/components/modules/FreshnessOverview'
import { AlertsPanel } from '@/components/modules/AlertsPanel'
import { QuickActions } from '@/components/modules/QuickActions'

export default function DashboardPage() {
  return (
    <div className="flex min-h-screen bg-dark-950">
      <Sidebar />

      <main className="flex-1 ml-64">
        <DashboardHeader />

        <div className="p-6 space-y-6">
          {/* KPI Cards Row */}
          <KPICards />

          {/* Main Content Grid */}
          <div className="grid grid-cols-12 gap-6">
            {/* Citation Trend Chart - Wide */}
            <div className="col-span-8">
              <CitationTrendChart />
            </div>

            {/* Alerts Panel */}
            <div className="col-span-4">
              <AlertsPanel />
            </div>
          </div>

          {/* Second Row */}
          <div className="grid grid-cols-12 gap-6">
            {/* Platform Breakdown */}
            <div className="col-span-4">
              <PlatformBreakdown />
            </div>

            {/* RRF Score Calculator */}
            <div className="col-span-4">
              <RRFScoreCard />
            </div>

            {/* Content Freshness */}
            <div className="col-span-4">
              <FreshnessOverview />
            </div>
          </div>

          {/* Quick Actions */}
          <QuickActions />
        </div>
      </main>
    </div>
  )
}
