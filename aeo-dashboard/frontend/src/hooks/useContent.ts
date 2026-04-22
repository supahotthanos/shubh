'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'

import { contentApi } from '@/lib/api'
import { queryKeys } from '@/lib/queryKeys'

export const useContent = (clientId: number | null) =>
  useQuery({
    queryKey: queryKeys.content(clientId ?? 0),
    queryFn: () => contentApi.list(clientId!).then((r) => r.data),
    enabled: !!clientId,
  })

export const useFreshnessSummary = (clientId: number | null) =>
  useQuery({
    queryKey: queryKeys.freshnessSummary(clientId ?? 0),
    queryFn: () => contentApi.getFreshnessSummary(clientId!).then((r) => r.data),
    enabled: !!clientId,
  })

export const useFreshnessTargets = () =>
  useQuery({
    queryKey: ['freshness-targets'],
    queryFn: () => contentApi.getFreshnessTargets().then((r) => r.data),
  })

export const useAddContent = (clientId: number | null) => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (url: string) => contentApi.add(clientId!, url),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.content(clientId ?? 0) })
      toast.success('URL added')
    },
    onError: () => toast.error('Failed to add URL'),
  })
}

export const useAnalyzeContent = (clientId: number | null) => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (contentId: number) => contentApi.analyze(contentId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.content(clientId ?? 0) })
      qc.invalidateQueries({ queryKey: queryKeys.freshnessSummary(clientId ?? 0) })
      toast.success('Content analyzed')
    },
    onError: () => toast.error('Analysis failed'),
  })
}
