'use client'

import { useRouter } from 'next/navigation'
import { useEffect, type ReactNode } from 'react'

import { useAuthStore } from '@/stores/authStore'

export function AuthGate({ children }: { children: ReactNode }) {
  const router = useRouter()
  const { token, hydrated } = useAuthStore()

  useEffect(() => {
    if (hydrated && !token) {
      router.replace('/login')
    }
  }, [hydrated, token, router])

  if (!hydrated) {
    return (
      <div className="min-h-screen bg-dark-950 flex items-center justify-center text-dark-400 text-sm">
        Loading…
      </div>
    )
  }
  if (!token) {
    return null
  }
  return <>{children}</>
}
