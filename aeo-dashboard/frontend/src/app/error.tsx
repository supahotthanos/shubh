'use client'

import { AlertTriangle } from 'lucide-react'
import { useEffect } from 'react'

import { Button } from '@/components/ui/Button'

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // eslint-disable-next-line no-console
    console.error(error)
  }, [error])

  return (
    <div className="min-h-screen flex items-center justify-center bg-dark-950 p-6">
      <div className="card max-w-md">
        <div className="flex items-center gap-3 mb-3">
          <div className="p-2 rounded-lg bg-red-500/10">
            <AlertTriangle className="w-5 h-5 text-red-400" />
          </div>
          <h2 className="card-title">Something went wrong</h2>
        </div>
        <p className="text-sm text-dark-400">
          {error?.message || 'An unexpected error occurred. Please try again.'}
        </p>
        <div className="mt-4 flex gap-2">
          <Button onClick={reset}>Try again</Button>
          <Button variant="ghost" onClick={() => (window.location.href = '/')}>
            Go home
          </Button>
        </div>
      </div>
    </div>
  )
}
