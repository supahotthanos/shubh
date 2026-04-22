'use client'

import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-dark-950 p-6">
      <div className="card max-w-md text-center">
        <p className="text-xs text-dark-500">404</p>
        <h1 className="text-xl font-bold text-white mt-1">Page not found</h1>
        <p className="text-sm text-dark-400 mt-2">The page you're looking for doesn't exist.</p>
        <Link href="/" className="btn btn-primary mt-4 inline-flex">
          Back to dashboard
        </Link>
      </div>
    </div>
  )
}
