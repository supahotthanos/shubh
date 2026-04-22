'use client'

import type { ReactNode } from 'react'

import { AuthGate } from './AuthGate'
import { Sidebar } from './Sidebar'

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <AuthGate>
      <div className="flex min-h-screen bg-dark-950">
        <Sidebar />
        <main className="flex-1 ml-64">
          <div className="p-6 space-y-6">{children}</div>
        </main>
      </div>
    </AuthGate>
  )
}
