'use client'

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { axisStyle, gridStyle, tooltipStyle, chartPalette } from './chartTheme'

interface Props {
  data: any[]
  xKey: string
  yKey: string
  height?: number
  color?: string
  label?: string
}

export function LineChart({ data, xKey, yKey, height = 240, color = chartPalette.primary, label }: Props) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
        <defs>
          <linearGradient id={`grad-${yKey}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={color} stopOpacity={0.35} />
            <stop offset="95%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid {...gridStyle} />
        <XAxis dataKey={xKey} {...axisStyle} />
        <YAxis {...axisStyle} />
        <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: '#f8fafc' }} />
        <Area
          type="monotone"
          dataKey={yKey}
          stroke={color}
          strokeWidth={2}
          fill={`url(#grad-${yKey})`}
          name={label ?? yKey}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
