'use client'

import { useQuery } from '@tanstack/react-query'

import { authorityApi } from '@/lib/api'
import { queryKeys } from '@/lib/queryKeys'

export const useAuthorityOverview = (clientId: number | null) =>
  useQuery({
    queryKey: queryKeys.authority(clientId ?? 0),
    queryFn: () => authorityApi.overview(clientId!).then((r) => r.data),
    enabled: !!clientId,
  })
