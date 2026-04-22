'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'

import { competitorsApi } from '@/lib/api'
import { queryKeys } from '@/lib/queryKeys'

export const useCompetitors = (clientId: number | null) =>
  useQuery({
    queryKey: queryKeys.competitors(clientId ?? 0),
    queryFn: () => competitorsApi.list(clientId!).then((r) => r.data),
    enabled: !!clientId,
  })

export const useCompetitorComparison = (clientId: number | null) =>
  useQuery({
    queryKey: queryKeys.competitorComparison(clientId ?? 0),
    queryFn: () => competitorsApi.getComparison(clientId!).then((r) => r.data),
    enabled: !!clientId,
  })

export const useCitationOverlap = (clientId: number | null, competitorId?: number) =>
  useQuery({
    queryKey: ['citation-overlap', clientId, competitorId ?? null],
    queryFn: () => competitorsApi.getCitationOverlap(clientId!, competitorId).then((r) => r.data),
    enabled: !!clientId,
  })

export const useAddCompetitor = (clientId: number | null) => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ name, domain }: { name: string; domain: string }) =>
      competitorsApi.add(clientId!, name, domain),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.competitors(clientId ?? 0) })
      toast.success('Competitor added')
    },
    onError: () => toast.error('Failed to add competitor'),
  })
}

export const useAnalyzeCompetitor = (clientId: number | null) => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (competitorId: number) => competitorsApi.analyze(competitorId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.competitors(clientId ?? 0) })
      toast.success('Competitor analyzed')
    },
    onError: () => toast.error('Analysis failed'),
  })
}
