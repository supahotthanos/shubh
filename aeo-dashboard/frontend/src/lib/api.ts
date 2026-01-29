import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Dashboard
export const dashboardApi = {
  getMetrics: (clientId: number) =>
    api.get(`/dashboard/metrics/${clientId}`),

  getPlatforms: (clientId: number) =>
    api.get(`/dashboard/platforms/${clientId}`),

  getCitationTrend: (clientId: number, period: string) =>
    api.get(`/dashboard/citations/trend/${clientId}?period=${period}`),

  getAlerts: (clientId: number) =>
    api.get(`/dashboard/alerts/${clientId}`),

  getQuickActions: (clientId: number) =>
    api.get(`/dashboard/quick-actions/${clientId}`),
}

// Citations
export const citationsApi = {
  list: (clientId: number, params?: Record<string, any>) =>
    api.get(`/citations/${clientId}`, { params }),

  getStats: (clientId: number, days?: number) =>
    api.get(`/citations/${clientId}/stats`, { params: { days } }),

  getTrend: (clientId: number, period: string) =>
    api.get(`/citations/${clientId}/trend`, { params: { period } }),

  getHeatmap: (clientId: number) =>
    api.get(`/citations/${clientId}/heatmap`),

  getPlatformStats: (clientId: number) =>
    api.get(`/citations/${clientId}/platforms`),
}

// Prompts
export const promptsApi = {
  list: (clientId: number, params?: Record<string, any>) =>
    api.get(`/prompts/${clientId}`, { params }),

  create: (clientId: number, data: any) =>
    api.post(`/prompts/${clientId}`, data),

  bulkImport: (clientId: number, prompts: string[]) =>
    api.post(`/prompts/${clientId}/bulk`, { prompts }),

  importFromGSC: (clientId: number, config: any) =>
    api.post(`/prompts/${clientId}/import-gsc`, config),

  checkVisibility: (promptId: number, config: any) =>
    api.post(`/prompts/${promptId}/check-visibility`, config),

  getVisibilitySummary: (clientId: number) =>
    api.get(`/prompts/${clientId}/visibility-summary`),
}

// Keywords & RRF
export const keywordsApi = {
  list: (clientId: number, priorityOnly?: boolean) =>
    api.get(`/keywords/${clientId}`, { params: { priority_only: priorityOnly } }),

  add: (clientId: number, data: any) =>
    api.post(`/keywords/${clientId}`, data),

  addBulk: (clientId: number, keywords: string[]) =>
    api.post(`/keywords/${clientId}/bulk`, { keywords }),

  getRRFScores: (clientId: number, belowThresholdOnly?: boolean) =>
    api.get(`/keywords/${clientId}/rrf-scores`, { params: { below_threshold_only: belowThresholdOnly } }),

  calculateRRF: (data: any) =>
    api.post(`/keywords/calculate-rrf`, data),

  getQuickReference: () =>
    api.get(`/keywords/rrf-quick-reference`),

  getRecommendations: (clientId: number, limit?: number) =>
    api.get(`/keywords/${clientId}/rrf-recommendations`, { params: { limit } }),

  simulateImprovement: (keywordId: number, newRank: number) =>
    api.post(`/keywords/${keywordId}/simulate-improvement`, null, { params: { new_rank: newRank } }),
}

// Content
export const contentApi = {
  list: (clientId: number, params?: Record<string, any>) =>
    api.get(`/content/${clientId}`, { params }),

  add: (clientId: number, url: string) =>
    api.post(`/content/${clientId}`, { url }),

  analyze: (contentId: number) =>
    api.post(`/content/${contentId}/analyze`),

  getFreshnessSummary: (clientId: number) =>
    api.get(`/content/${clientId}/freshness-summary`),

  getFreshnessTargets: () =>
    api.get(`/content/freshness-targets`),

  getOptimizationRecommendations: (contentId: number) =>
    api.get(`/content/${contentId}/optimization-recommendations`),
}

// Campaigns
export const campaignsApi = {
  list: (clientId: number, params?: Record<string, any>) =>
    api.get(`/campaigns/${clientId}`, { params }),

  create: (clientId: number, data: any) =>
    api.post(`/campaigns/${clientId}`, data),

  update: (campaignId: number, data: any) =>
    api.patch(`/campaigns/${campaignId}`, data),

  addAsset: (campaignId: number, data: any) =>
    api.post(`/campaigns/${campaignId}/assets`, data),

  listAssets: (campaignId: number, status?: string) =>
    api.get(`/campaigns/${campaignId}/assets`, { params: { status } }),

  updateAssetStatus: (assetId: number, status: string) =>
    api.patch(`/campaigns/${assetId}/status`, null, { params: { status } }),

  getSummary: (clientId: number) =>
    api.get(`/campaigns/${clientId}/summary`),

  getMetrics: (campaignId: number, days?: number) =>
    api.get(`/campaigns/${campaignId}/metrics`, { params: { days } }),
}

// Competitors
export const competitorsApi = {
  list: (clientId: number) =>
    api.get(`/competitors/${clientId}`),

  add: (clientId: number, data: any) =>
    api.post(`/competitors/${clientId}`, data),

  getComparison: (clientId: number) =>
    api.get(`/competitors/${clientId}/comparison`),

  getCitationOverlap: (clientId: number, competitorId?: number) =>
    api.get(`/competitors/${clientId}/citation-overlap`, { params: { competitor_id: competitorId } }),

  getAuthorityComparison: (clientId: number) =>
    api.get(`/competitors/${clientId}/authority-comparison`),

  analyze: (competitorId: number) =>
    api.post(`/competitors/${competitorId}/analyze`),
}

// Reports
export const reportsApi = {
  list: (clientId: number, reportType?: string) =>
    api.get(`/reports/${clientId}`, { params: { report_type: reportType } }),

  generate: (clientId: number, reportType: string, periodStart?: string, periodEnd?: string) =>
    api.post(`/reports/${clientId}/generate`, null, {
      params: { report_type: reportType, period_start: periodStart, period_end: periodEnd },
    }),

  download: (reportId: number, format: 'pdf' | 'csv') =>
    api.get(`/reports/${reportId}/download`, {
      params: { format },
      responseType: format === 'pdf' ? 'blob' : 'text',
    }),

  getSlidesOutline: (reportId: number) =>
    api.get(`/reports/${reportId}/slides`),

  listSchedules: (clientId: number) =>
    api.get(`/reports/${clientId}/schedules`),

  createSchedule: (clientId: number, data: any) =>
    api.post(`/reports/${clientId}/schedules`, data),
}

export default api
