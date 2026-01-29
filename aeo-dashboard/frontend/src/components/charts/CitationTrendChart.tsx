'use client'

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'

// Sample data - would come from API
const data = [
  { date: 'Jan 1', citations: 95, stability: 72 },
  { date: 'Jan 5', citations: 98, stability: 74 },
  { date: 'Jan 10', citations: 102, stability: 73 },
  { date: 'Jan 15', citations: 108, stability: 76 },
  { date: 'Jan 20', citations: 115, stability: 78 },
  { date: 'Jan 25', citations: 125, stability: 77 },
  { date: 'Jan 30', citations: 142, stability: 79 },
]

export function CitationTrendChart() {
  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h2 className="card-title">Citation Trend</h2>
          <p className="text-sm text-dark-400 mt-1">
            Citations and stability over time
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-primary-500 rounded-full"></div>
            <span className="text-sm text-dark-400">Citations</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-sm text-dark-400">Stability %</span>
          </div>
        </div>
      </div>

      <div className="h-80 mt-4">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="citationGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="stabilityGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis
              dataKey="date"
              stroke="#64748b"
              tick={{ fill: '#64748b', fontSize: 12 }}
            />
            <YAxis
              yAxisId="left"
              stroke="#64748b"
              tick={{ fill: '#64748b', fontSize: 12 }}
            />
            <YAxis
              yAxisId="right"
              orientation="right"
              stroke="#64748b"
              tick={{ fill: '#64748b', fontSize: 12 }}
              domain={[0, 100]}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: '1px solid #334155',
                borderRadius: '8px',
              }}
              labelStyle={{ color: '#f8fafc' }}
            />
            <Area
              yAxisId="left"
              type="monotone"
              dataKey="citations"
              stroke="#6366f1"
              strokeWidth={2}
              fill="url(#citationGradient)"
            />
            <Area
              yAxisId="right"
              type="monotone"
              dataKey="stability"
              stroke="#22c55e"
              strokeWidth={2}
              fill="url(#stabilityGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
