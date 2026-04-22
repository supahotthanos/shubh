'use client'

import { useQuery } from '@tanstack/react-query'

import { citationsApi } from '@/lib/api'
import { queryKeys } from '@/lib/queryKeys'

export const useCitations = (clientId: number | null, params?: Record<string, any>) =>
  useQuery({
    queryKey: queryKeys.citations(clientId ?? 0, params),
    queryFn: () => citationsApi.list(clientId!, params).then((r) => r.data),
    enabled: !!clientId,
  })

export const useCitationStats = (clientId: number | null, days = 30) =>
  useQuery({
    queryKey: queryKeys.citationStats(clientId ?? 0, days),
    queryFn: () => citationsApi.getStats(clientId!, days).then((r) => r.data),
    enabled: !!clientId,
  })

export const useCitationPlatformStats = (clientId: number | null) =>
  useQuery({
    queryKey: [...queryKeys.citationStats(clientId ?? 0, 0), 'platforms'],
    queryFn: () => citationsApi.getPlatformStats(clientId!).then((r) => r.data),
    enabled: !!clientId,
  })
