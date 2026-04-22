'use client'

import { AlertTriangle, CheckCircle2, ExternalLink } from 'lucide-react'

import { AppShell } from '@/components/ui/AppShell'
import { Badge } from '@/components/ui/Badge'
import { DashboardHeader } from '@/components/ui/DashboardHeader'
import { EmptyState } from '@/components/ui/EmptyState'
import { PageHeader } from '@/components/ui/PageHeader'
import { Skeleton } from '@/components/ui/Skeleton'
import { useAuthorityOverview } from '@/hooks/useAuthority'
import { useClientStore } from '@/stores/clientStore'

export default function AuthorityPage() {
  const { activeClientId } = useClientStore()
  const { data, isLoading } = useAuthorityOverview(activeClientId)

  return (
    <AppShell>
      <DashboardHeader
        title="Authority"
        description="Common Crawl WebGraph, Ahrefs DR, Moz DA, Wikipedia citations"
      />
      <PageHeader title="Domain authority signals" />

      {isLoading ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Skeleton className="h-56 w-full" />
          <Skeleton className="h-56 w-full" />
        </div>
      ) : !data?.domains?.length ? (
        <EmptyState
          title="No domains"
          description="Add at least one domain to this client to see authority signals."
        />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {data.domains.map((d: any) => (
            <div key={d.domain} className="card">
              <div className="card-header">
                <div>
                  <h2 className="card-title">{d.domain}</h2>
                  <p className="text-xs text-dark-500 mt-1">
                    {d.is_primary ? 'Primary domain' : 'Secondary domain'}
                  </p>
                </div>
                {d.warnings?.authority_dilution ? (
                  <Badge tone="warning">Dilution warning</Badge>
                ) : (
                  <Badge tone="success">Direct authority</Badge>
                )}
              </div>

              <div className="grid grid-cols-2 gap-3 mt-4 text-sm">
                <Stat label="Harmonic centrality rank" value={d.metrics.hc_rank?.toLocaleString()} />
                <Stat label="PageRank rank" value={d.metrics.pagerank_rank?.toLocaleString()} />
                <Stat label="Ahrefs DR" value={d.metrics.domain_rating?.toFixed(1)} />
                <Stat label="Moz DA" value={d.metrics.domain_authority?.toFixed(1)} />
                <Stat label="Referring domains" value={d.metrics.referring_domains?.toLocaleString()} />
                <Stat label="Total backlinks" value={d.metrics.total_backlinks?.toLocaleString()} />
              </div>

              <div className="mt-4 p-3 bg-dark-800 rounded-lg">
                <div className="flex items-center gap-2 text-sm">
                  {d.metrics.has_wikipedia_citation ? (
                    <CheckCircle2 className="w-4 h-4 text-green-400" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 text-yellow-400" />
                  )}
                  <span className="text-white">
                    {d.metrics.has_wikipedia_citation ? 'Cited on Wikipedia' : 'Not cited on Wikipedia'}
                  </span>
                </div>
                {d.metrics.has_wikipedia_citation && d.metrics.wikipedia_url && (
                  <a
                    href={d.metrics.wikipedia_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 mt-1 text-xs text-primary-400"
                  >
                    View citation <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>

              {d.warnings?.authority_dilution && (
                <p className="mt-3 text-xs text-yellow-400">{d.warnings.explanation}</p>
              )}

              {d.recommendations?.length > 0 && (
                <div className="mt-4 space-y-2">
                  <p className="text-xs text-dark-400">Recommendations</p>
                  {d.recommendations.map((rec: any, idx: number) => (
                    <div key={idx} className="p-3 rounded-lg bg-dark-800 border border-dark-700">
                      <div className="flex items-center justify-between">
                        <p className="text-sm text-white">{rec.title}</p>
                        <Badge
                          tone={
                            rec.priority === 'critical'
                              ? 'danger'
                              : rec.priority === 'high'
                                ? 'warning'
                                : 'info'
                          }
                        >
                          {rec.priority}
                        </Badge>
                      </div>
                      <p className="text-xs text-dark-400 mt-1">{rec.description}</p>
                      <p className="text-xs text-primary-300 mt-1">{rec.action}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </AppShell>
  )
}

function Stat({ label, value }: { label: string; value?: string | number | null }) {
  return (
    <div>
      <p className="text-xs text-dark-500">{label}</p>
      <p className="text-base text-white font-medium">{value ?? '—'}</p>
    </div>
  )
}
