'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'

import { promptsApi } from '@/lib/api'
import { queryKeys } from '@/lib/queryKeys'

export const usePrompts = (clientId: number | null, params?: Record<string, any>) =>
  useQuery({
    queryKey: queryKeys.prompts(clientId ?? 0, params),
    queryFn: () => promptsApi.list(clientId!, params).then((r) => r.data),
    enabled: !!clientId,
  })

export const useCreatePrompt = (clientId: number | null) => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (text: string) => promptsApi.create(clientId!, { text }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['prompts', clientId] })
      toast.success('Prompt added')
    },
    onError: () => toast.error('Failed to add prompt'),
  })
}

export const useCheckVisibility = () =>
  useMutation({
    mutationFn: (args: { promptId: number; platforms?: string[]; checkCount?: number }) =>
      promptsApi.checkVisibility(args.promptId, {
        prompt_id: args.promptId,
        platforms: args.platforms ?? ['chatgpt', 'perplexity', 'claude', 'google_ai'],
        check_count: args.checkCount ?? 1,
      }),
    onSuccess: () => toast.success('Visibility check complete'),
    onError: () => toast.error('Visibility check failed'),
  })

export const useImportFromGSC = (clientId: number | null) => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (config: any) => promptsApi.importFromGSC(clientId!, config),
    onSuccess: (res) => {
      qc.invalidateQueries({ queryKey: ['prompts', clientId] })
      toast.success(`Imported ${res.data.imported_prompts} prompts`)
    },
    onError: () => toast.error('GSC import failed'),
  })
}
