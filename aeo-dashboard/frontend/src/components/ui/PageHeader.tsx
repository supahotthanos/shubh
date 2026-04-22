'use client'

import type { ReactNode } from 'react'

interface Props {
  title: string
  description?: string
  actions?: ReactNode
  filters?: ReactNode
}

export function PageHeader({ title, description, actions, filters }: Props) {
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">{title}</h1>
          {description && <p className="text-sm text-dark-400 mt-1">{description}</p>}
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>
      {filters && <div className="flex flex-wrap items-center gap-2">{filters}</div>}
    </div>
  )
}
