'use client'

import { useQuery } from '@tanstack/react-query'

import { dashboardApi } from '@/lib/api'
import { queryKeys } from '@/lib/queryKeys'

export const useDashboardMetrics = (clientId: number | null, period = '30d') =>
  useQuery({
    queryKey: queryKeys.dashboard(clientId ?? 0, period),
    queryFn: () => dashboardApi.getMetrics(clientId!).then((r) => r.data),
    enabled: !!clientId,
  })

export const usePlatformBreakdown = (clientId: number | null) =>
  useQuery({
    queryKey: queryKeys.platforms(clientId ?? 0),
    queryFn: () => dashboardApi.getPlatforms(clientId!).then((r) => r.data),
    enabled: !!clientId,
  })

export const useCitationTrend = (clientId: number | null, period = '30d') =>
  useQuery({
    queryKey: [...queryKeys.dashboard(clientId ?? 0, period), 'trend'],
    queryFn: () => dashboardApi.getCitationTrend(clientId!, period).then((r) => r.data),
    enabled: !!clientId,
  })

export const useDashboardAlerts = (clientId: number | null) =>
  useQuery({
    queryKey: queryKeys.alerts(clientId ?? 0),
    queryFn: () => dashboardApi.getAlerts(clientId!).then((r) => r.data),
    enabled: !!clientId,
  })

export const useQuickActions = (clientId: number | null) =>
  useQuery({
    queryKey: queryKeys.quickActions(clientId ?? 0),
    queryFn: () => dashboardApi.getQuickActions(clientId!).then((r) => r.data),
    enabled: !!clientId,
  })
