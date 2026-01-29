// Dashboard Types
export interface TrendIndicator {
  value: number
  change: number
  changePercentage: number
  trend: 'up' | 'down' | 'stable'
  period: string
}

export interface DashboardMetrics {
  totalCitations: number
  citationsTrend: TrendIndicator
  citationStabilityScore: number
  stabilityTrend: TrendIndicator
  rrfVisibilityScore: number
  rrfTrend: TrendIndicator
  keywordsMeetingThreshold: number
  keywordsTotal: number
  contentFreshnessGrade: string
  contentFreshnessScore: number
  pagesNeedingRefresh: number
  activeCampaigns: number
  campaignBreakdown: Record<string, number>
  competitivePosition: number
  shareOfVoice: number
  promptsVisible: number
  promptsTotal: number
  promptCoveragePercentage: number
}

export interface PlatformBreakdown {
  platformName: string
  platformSlug: string
  iconUrl?: string
  totalCitations: number
  activeCitations: number
  avgPosition: number
  stabilityScore: number
  trend: 'up' | 'down' | 'stable'
  trendValue: number
}

// Citation Types
export interface Citation {
  id: number
  promptId: number
  promptText?: string
  platformId: number
  platformName?: string
  citedUrl?: string
  citedText?: string
  mentionType: 'linked' | 'unlinked' | 'brand_mention'
  position?: number
  isPrimary: boolean
  contextSnippet?: string
  confidenceScore?: number
  sentiment?: string
  firstSeenAt?: string
  lastSeenAt?: string
  isCurrentlyVisible: boolean
  createdAt: string
}

export interface CitationStats {
  totalCitations: number
  activeCitations: number
  linkedMentions: number
  unlinkedMentions: number
  brandMentions: number
  byPlatform: Record<string, number>
  byPosition: Record<string, number>
  avgPosition: number
  citationStabilityScore: number
}

// Prompt Types
export interface Prompt {
  id: number
  text: string
  normalizedText?: string
  source: string
  intentType?: string
  isBranded: boolean
  gscImpressions?: number
  gscClicks?: number
  gscAvgPosition?: number
  isVisible?: boolean
  visibilityScore?: number
  lastCheckedAt?: string
  checkFrequencyHours: number
  categoryId?: number
  categoryName?: string
  createdAt: string
  updatedAt: string
}

// Keyword & RRF Types
export interface Keyword {
  id: number
  keyword: string
  normalizedKeyword?: string
  monthlySearchVolume?: number
  keywordDifficulty?: number
  cpc?: number
  searchIntent?: string
  isPriority: boolean
  trackRankings: boolean
  rrfScore?: number
  rrfMeetsThreshold?: boolean
  createdAt: string
  updatedAt: string
}

export interface RRFScore {
  id: number
  keywordId: number
  keywordText?: string
  subQueries: SubQueryRank[]
  kConstant: number
  rawScore: number
  normalizedScore: number
  meetsThreshold: boolean
  totalAppearances: number
  avgRank: number
  bestRank: number
  worstRank: number
  appearancesNeeded: number
  targetRankEach: number
  calculatedAt: string
}

export interface SubQueryRank {
  query: string
  rank: number
  url: string
  searchEngine: string
}

export interface RRFQuickReference {
  appearances: number
  maxRankEach: number
  guaranteedScore: number
  meetsThreshold: boolean
}

// Content Types
export interface TrackedContent {
  id: number
  url: string
  title?: string
  metaDescription?: string
  wordCount?: number
  avgChunkSizeTokens?: number
  hasSchemaMarkup: boolean
  schemaTypes?: string[]
  headingStructure?: Record<string, any>
  hasPaaStyleSections: boolean
  hasNegationContent: boolean
  isActive: boolean
  checkFrequencyHours: number
  freshnessScore?: number
  freshnessGrade?: string
  daysSinceUpdate?: number
  createdAt: string
  updatedAt: string
}

export interface FreshnessAnalysis {
  url: string
  freshnessScore: number
  freshnessGrade: 'A' | 'B' | 'C' | 'D' | 'F'
  daysSinceUpdate: number
  gptImpact: string
  llamaImpact: string
  geminiImpact: string
  estimatedPositionLoss: number
  refreshPriority: 'critical' | 'high' | 'medium' | 'low'
  recommendations: string[]
}

// Campaign Types
export interface Campaign {
  id: number
  name: string
  campaignType: string
  description?: string
  status: string
  startDate?: string
  endDate?: string
  targetCitations?: number
  targetDomains?: number
  targetPrompts?: string[]
  budget?: number
  spent: number
  totalAssets: number
  liveAssets: number
  citingAssets: number
  totalCitationsGained: number
  createdAt: string
  updatedAt: string
}

export interface CampaignAsset {
  id: number
  assetType: string
  title: string
  url?: string
  hostingDomain?: string
  hostingDomainAuthority?: number
  clientPosition?: number
  totalItems?: number
  status: string
  publishedAt?: string
  indexedAt?: string
  firstCitationAt?: string
  citationCount: number
  promptsCitedFor?: string[]
  createdAt: string
}

// Competitor Types
export interface Competitor {
  id: number
  name: string
  domain: string
  brandNames: string[]
  totalCitations: number
  citationShare: number
  avgPosition?: number
  harmonicCentralityRank?: number
  domainRating?: number
  isActive: boolean
  lastAnalyzedAt?: string
}

// Report Types
export interface Report {
  id: number
  title: string
  reportType: string
  periodStart: string
  periodEnd: string
  summaryMetrics: Record<string, any>
  generatedAt: string
  status: string
  pdfUrl?: string
}

// Alert Types
export interface Alert {
  id: string
  type: string
  severity: 'critical' | 'warning' | 'info'
  title: string
  description: string
  actionUrl?: string
  createdAt: string
}

// Quick Action Types
export interface QuickAction {
  id: string
  title: string
  description: string
  actionType: string
  priority: number
  estimatedImpact: 'high' | 'medium' | 'low'
}
