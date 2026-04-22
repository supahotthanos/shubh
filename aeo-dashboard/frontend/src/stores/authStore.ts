'use client'

import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

export interface AuthUser {
  id: number
  email: string
  full_name?: string | null
  role: string
  organization_id: number
}

interface AuthState {
  token: string | null
  user: AuthUser | null
  hydrated: boolean
  setAuth: (token: string, user: AuthUser) => void
  logout: () => void
  markHydrated: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      hydrated: false,
      setAuth: (token, user) => set({ token, user }),
      logout: () => set({ token: null, user: null }),
      markHydrated: () => set({ hydrated: true }),
    }),
    {
      name: 'aeo-auth',
      storage: createJSONStorage(() => localStorage),
      onRehydrateStorage: () => (state) => state?.markHydrated(),
      partialize: (state) => ({ token: state.token, user: state.user }),
    },
  ),
)
