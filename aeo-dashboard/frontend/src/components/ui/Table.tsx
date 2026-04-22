'use client'

import { clsx } from 'clsx'
import type { ReactNode } from 'react'

import { SkeletonRow } from './Skeleton'
import { EmptyState } from './EmptyState'

export interface Column<T> {
  key: string
  header: string
  align?: 'left' | 'right' | 'center'
  className?: string
  render: (row: T, index: number) => ReactNode
}

interface TableProps<T> {
  columns: Column<T>[]
  rows: T[] | undefined
  isLoading?: boolean
  emptyTitle?: string
  emptyDescription?: string
  onRowClick?: (row: T) => void
  rowKey: (row: T, index: number) => string | number
}

export function Table<T>({
  columns,
  rows,
  isLoading,
  emptyTitle = 'No results',
  emptyDescription,
  onRowClick,
  rowKey,
}: TableProps<T>) {
  return (
    <div className="card overflow-hidden p-0">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-dark-900/80 text-left text-xs uppercase tracking-wider text-dark-400">
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={clsx(
                    'px-4 py-3 font-medium',
                    col.align === 'right' && 'text-right',
                    col.align === 'center' && 'text-center',
                    col.className,
                  )}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {isLoading && (
              <>
                <SkeletonRow cols={columns.length} />
                <SkeletonRow cols={columns.length} />
                <SkeletonRow cols={columns.length} />
              </>
            )}
            {!isLoading && rows && rows.length === 0 && (
              <tr>
                <td colSpan={columns.length} className="px-0 py-0">
                  <EmptyState title={emptyTitle} description={emptyDescription} />
                </td>
              </tr>
            )}
            {!isLoading &&
              rows?.map((row, index) => (
                <tr
                  key={rowKey(row, index)}
                  onClick={onRowClick ? () => onRowClick(row) : undefined}
                  className={clsx(
                    'border-t border-dark-800 transition-colors',
                    onRowClick && 'cursor-pointer hover:bg-dark-900',
                  )}
                >
                  {columns.map((col) => (
                    <td
                      key={col.key}
                      className={clsx(
                        'px-4 py-3 text-dark-200',
                        col.align === 'right' && 'text-right',
                        col.align === 'center' && 'text-center',
                        col.className,
                      )}
                    >
                      {col.render(row, index)}
                    </td>
                  ))}
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
