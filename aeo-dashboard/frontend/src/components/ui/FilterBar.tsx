'use client'

import { clsx } from 'clsx'

export interface ChipOption {
  value: string
  label: string
  count?: number
}

interface FilterChipsProps {
  options: ChipOption[]
  value?: string | null
  onChange: (value: string | null) => void
  allowClear?: boolean
}

export function FilterChips({ options, value, onChange, allowClear = true }: FilterChipsProps) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      {allowClear && (
        <button
          onClick={() => onChange(null)}
          className={clsx(
            'px-3 py-1.5 rounded-full text-xs font-medium transition-colors border',
            !value
              ? 'bg-primary-600 text-white border-primary-500'
              : 'bg-dark-800 text-dark-300 border-dark-700 hover:text-white',
          )}
        >
          All
        </button>
      )}
      {options.map((opt) => {
        const isActive = value === opt.value
        return (
          <button
            key={opt.value}
            onClick={() => onChange(opt.value)}
            className={clsx(
              'px-3 py-1.5 rounded-full text-xs font-medium transition-colors border',
              isActive
                ? 'bg-primary-600 text-white border-primary-500'
                : 'bg-dark-800 text-dark-300 border-dark-700 hover:text-white',
            )}
          >
            {opt.label}
            {opt.count !== undefined && (
              <span className="ml-1 opacity-70">· {opt.count}</span>
            )}
          </button>
        )
      })}
    </div>
  )
}
