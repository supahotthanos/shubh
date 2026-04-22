'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'

import { campaignsApi } from '@/lib/api'
import { queryKeys } from '@/lib/queryKeys'

export const useCampaigns = (clientId: number | null) =>
  useQuery({
    queryKey: queryKeys.campaigns(clientId ?? 0),
    queryFn: () => campaignsApi.list(clientId!).then((r) => r.data),
    enabled: !!clientId,
  })

export const useCampaignSummary = (clientId: number | null) =>
  useQuery({
    queryKey: ['campaign-summary', clientId],
    queryFn: () => campaignsApi.getSummary(clientId!).then((r) => r.data),
    enabled: !!clientId,
  })

export const useCreateCampaign = (clientId: number | null) => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: any) => campaignsApi.create(clientId!, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.campaigns(clientId ?? 0) })
      toast.success('Campaign created')
    },
    onError: () => toast.error('Failed to create campaign'),
  })
}

export const useUpdateAssetStatus = (campaignId: number | null) => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ assetId, status }: { assetId: number; status: string }) =>
      campaignsApi.updateAssetStatus(assetId, status),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.campaignAssets(campaignId ?? 0) })
    },
  })
}
