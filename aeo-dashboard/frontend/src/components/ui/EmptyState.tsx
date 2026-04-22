'use client'

import { Inbox } from 'lucide-react'
import type { ReactNode } from 'react'

interface Props {
  icon?: ReactNode
  title: string
  description?: string
  action?: ReactNode
}

export function EmptyState({ icon, title, description, action }: Props) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-12 px-6 rounded-xl border border-dashed border-dark-700 bg-dark-900/40">
      <div className="w-12 h-12 rounded-xl bg-dark-800 text-primary-300 flex items-center justify-center mb-4">
        {icon ?? <Inbox className="w-6 h-6" />}
      </div>
      <h3 className="text-base font-semibold text-white">{title}</h3>
      {description && (
        <p className="text-sm text-dark-400 mt-1 max-w-sm">{description}</p>
      )}
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}
