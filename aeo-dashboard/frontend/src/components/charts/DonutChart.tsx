'use client'

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'

import { chartColors, tooltipStyle } from './chartTheme'

interface Props {
  data: { name: string; value: number }[]
  height?: number
  innerRadius?: number
  outerRadius?: number
}

export function DonutChart({ data, height = 220, innerRadius = 60, outerRadius = 90 }: Props) {
  const total = data.reduce((acc, d) => acc + d.value, 0)
  return (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: '#f8fafc' }} />
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          innerRadius={innerRadius}
          outerRadius={outerRadius}
          paddingAngle={2}
          stroke="none"
        >
          {data.map((_, i) => (
            <Cell key={i} fill={chartColors[i % chartColors.length]} />
          ))}
        </Pie>
      </PieChart>
    </ResponsiveContainer>
  )
}
