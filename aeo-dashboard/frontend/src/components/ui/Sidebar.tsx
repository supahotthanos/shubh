'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  MessageSquare,
  Search,
  FileText,
  Target,
  Users,
  BarChart3,
  Settings,
  HelpCircle,
  Zap,
} from 'lucide-react'
import { clsx } from 'clsx'

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Citations', href: '/citations', icon: MessageSquare },
  { name: 'Prompts', href: '/prompts', icon: Search },
  { name: 'Keywords & RRF', href: '/keywords', icon: Target },
  { name: 'Content', href: '/content', icon: FileText },
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

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-dark-900 border-r border-dark-800 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-dark-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
            <Zap className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-white">AEO Dashboard</h1>
            <p className="text-xs text-dark-500">AI Citation Tracking</p>
          </div>
        </div>
      </div>

      {/* Client Selector */}
      <div className="p-4 border-b border-dark-800">
        <select className="w-full px-3 py-2 bg-dark-800 border border-dark-700 rounded-lg text-white text-sm">
          <option>Acme Corporation</option>
          <option>TechStart Inc</option>
          <option>Global Solutions</option>
        </select>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={clsx(
                'sidebar-link',
                isActive && 'active'
              )}
            >
              <item.icon className="w-5 h-5" />
              <span>{item.name}</span>
            </Link>
          )
        })}
      </nav>

      {/* Secondary Nav */}
      <div className="p-4 border-t border-dark-800">
        {secondaryNav.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className="sidebar-link"
          >
            <item.icon className="w-5 h-5" />
            <span>{item.name}</span>
          </Link>
        ))}
      </div>
    </aside>
  )
}
