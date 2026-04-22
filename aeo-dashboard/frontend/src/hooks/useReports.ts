'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'

import { reportsApi } from '@/lib/api'
import { queryKeys } from '@/lib/queryKeys'

export const useReports = (clientId: number | null) =>
  useQuery({
    queryKey: queryKeys.reports(clientId ?? 0),
    queryFn: () => reportsApi.list(clientId!).then((r) => r.data),
    enabled: !!clientId,
  })

export const useReportSchedules = (clientId: number | null) =>
  useQuery({
    queryKey: queryKeys.schedules(clientId ?? 0),
    queryFn: () => reportsApi.listSchedules(clientId!).then((r) => r.data),
    enabled: !!clientId,
  })

export const useGenerateReport = (clientId: number | null) => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (reportType: string) => reportsApi.generate(clientId!, reportType),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.reports(clientId ?? 0) })
      toast.success('Report generated')
    },
    onError: () => toast.error('Report generation failed'),
  })
}

export const useDownloadReport = () =>
  useMutation({
    mutationFn: async ({ id, format }: { id: number; format: 'pdf' | 'csv' }) => {
      const res = await reportsApi.download(id, format)
      const blob = new Blob([res.data], {
        type: format === 'pdf' ? 'application/pdf' : 'text/csv',
      })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `report_${id}.${format}`
      link.click()
      URL.revokeObjectURL(url)
    },
    onError: () => toast.error('Download failed'),
  })
