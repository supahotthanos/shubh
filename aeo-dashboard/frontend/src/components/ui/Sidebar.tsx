'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import {
  BarChart3,
  FileText,
  HelpCircle,
  LayoutDashboard,
  LogOut,
  MessageSquare,
  Search,
  Settings,
  Shield,
  Target,
  Users,
  Zap,
} from 'lucide-react'
import { clsx } from 'clsx'
import { useEffect } from 'react'

import { clientsApi } from '@/lib/api'
import { useAuthStore } from '@/stores/authStore'
import { useClientStore } from '@/stores/clientStore'

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Citations', href: '/citations', icon: MessageSquare },
  { name: 'Prompts', href: '/prompts', icon: Search },
  { name: 'Keywords & RRF', href: '/keywords', icon: Target },
  { name: 'Content', href: '/content', icon: FileText },
  { name: 'Authority', href: '/authority', icon: Shield },
  { name: 'Campaigns', href: '/campaigns', icon: Zap },
  { name: 'Competitors', href: '/competitors', icon: Users },
  { name: 'Reports', href: '/reports', icon: BarChart3 },
]

const secondaryNav = [
  { name: 'Settings', href: '/settings', icon: Settings },
  { name: 'Help', href: '/help', icon: HelpCircle },
]

export function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const { logout, user } = useAuthStore()
  const { clients, activeClientId, setActive, setClients } = useClientStore()

  useEffect(() => {
    clientsApi
      .list({ page_size: 100 })
      .then((res) =>
        setClients(
          (res.data.items ?? []).map((c: any) => ({ id: c.id, name: c.name, slug: c.slug })),
        ),
      )
      .catch(() => setClients([]))
  }, [setClients])

  const onLogout = () => {
    logout()
    router.replace('/login')
  }

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-dark-900 border-r border-dark-800 flex flex-col z-20">
      <div className="p-6 border-b border-dark-800">
        <Link href="/" className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
            <Zap className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-white">AEO Dashboard</h1>
            <p className="text-xs text-dark-500">AI Citation Tracking</p>
          </div>
        </Link>
      </div>

      <div className="p-4 border-b border-dark-800">
        <label className="text-xs uppercase text-dark-500 tracking-wider">Client</label>
        <select
          className="w-full mt-2 px-3 py-2 bg-dark-800 border border-dark-700 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          value={activeClientId ?? ''}
          onChange={(e) => setActive(Number(e.target.value))}
        >
          {clients.length === 0 && <option value="">No clients yet</option>}
          {clients.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
      </div>

      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {navigation.map((item) => {
          const isActive =
            item.href === '/' ? pathname === '/' : pathname?.startsWith(item.href)
          return (
            <Link
              key={item.name}
              href={item.href}
              className={clsx('sidebar-link', isActive && 'active')}
            >
              <item.icon className="w-5 h-5" />
              <span>{item.name}</span>
            </Link>
          )
        })}
      </nav>

      <div className="p-4 border-t border-dark-800 space-y-1">
        {secondaryNav.map((item) => (
          <Link key={item.name} href={item.href} className="sidebar-link">
            <item.icon className="w-5 h-5" />
            <span>{item.name}</span>
          </Link>
        ))}
        <button onClick={onLogout} className="sidebar-link w-full text-left">
          <LogOut className="w-5 h-5" />
          <span>Log out</span>
        </button>
        {user && (
          <div className="mt-2 text-xs text-dark-500 px-2">
            Signed in as <span className="text-dark-300">{user.email}</span>
          </div>
        )}
      </div>
    </aside>
  )
}
