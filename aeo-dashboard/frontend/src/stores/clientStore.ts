'use client'

import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

export interface ClientOption {
  id: number
  name: string
  slug: string
}

interface ClientState {
  activeClientId: number | null
  clients: ClientOption[]
  setActive: (id: number) => void
  setClients: (clients: ClientOption[]) => void
}

export const useClientStore = create<ClientState>()(
  persist(
    (set) => ({
      activeClientId: null,
      clients: [],
      setActive: (id) => set({ activeClientId: id }),
      setClients: (clients) =>
        set((state) => ({
          clients,
          activeClientId:
            state.activeClientId && clients.find((c) => c.id === state.activeClientId)
              ? state.activeClientId
              : clients[0]?.id ?? null,
        })),
    }),
    {
      name: 'aeo-active-client',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ activeClientId: state.activeClientId }),
    },
  ),
)
