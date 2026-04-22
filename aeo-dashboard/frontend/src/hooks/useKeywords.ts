'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'

import { keywordsApi } from '@/lib/api'
import { queryKeys } from '@/lib/queryKeys'

export const useKeywords = (clientId: number | null) =>
  useQuery({
    queryKey: queryKeys.keywords(clientId ?? 0),
    queryFn: () => keywordsApi.list(clientId!).then((r) => r.data),
    enabled: !!clientId,
  })

export const useRRFScores = (clientId: number | null) =>
  useQuery({
    queryKey: queryKeys.rrfScores(clientId ?? 0),
    queryFn: () => keywordsApi.getRRFScores(clientId!).then((r) => r.data),
    enabled: !!clientId,
  })

export const useRRFQuickReference = () =>
  useQuery({
    queryKey: queryKeys.rrfQuickRef(),
    queryFn: () => keywordsApi.getQuickReference().then((r) => r.data),
  })

export const useRRFRecommendations = (clientId: number | null) =>
  useQuery({
    queryKey: queryKeys.rrfRecs(clientId ?? 0),
    queryFn: () => keywordsApi.getRecommendations(clientId!, 10).then((r) => r.data),
    enabled: !!clientId,
  })

export const useAddKeyword = (clientId: number | null) => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (keyword: string) =>
      keywordsApi.add(clientId!, { keyword, is_priority: false }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.keywords(clientId ?? 0) })
      toast.success('Keyword added')
    },
    onError: () => toast.error('Failed to add keyword'),
  })
}

export const useSimulateImprovement = () =>
  useMutation({
    mutationFn: ({ keywordId, newRank }: { keywordId: number; newRank: number }) =>
      keywordsApi.simulateImprovement(keywordId, newRank).then((r) => r.data),
  })
