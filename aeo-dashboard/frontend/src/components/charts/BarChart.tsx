'use client'

import {
  Bar,
  BarChart as RBarChart,
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
  color?: string
  height?: number
}

export function BarChart({ data, xKey, yKey, color = chartPalette.primary, height = 240 }: Props) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <RBarChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
        <CartesianGrid {...gridStyle} />
        <XAxis dataKey={xKey} {...axisStyle} />
        <YAxis {...axisStyle} />
        <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: '#f8fafc' }} />
        <Bar dataKey={yKey} fill={color} radius={[4, 4, 0, 0]} />
      </RBarChart>
    </ResponsiveContainer>
  )
}
