'use client'

import { useRouter } from 'next/navigation'
import { FormEvent, useEffect, useState } from 'react'
import { Zap } from 'lucide-react'
import { toast } from 'sonner'

import { Button } from '@/components/ui/Button'
import { authApi } from '@/lib/api'
import { useAuthStore } from '@/stores/authStore'

export default function LoginPage() {
  const router = useRouter()
  const { setAuth, token, hydrated } = useAuthStore()
  const [email, setEmail] = useState('demo@aeo.local')
  const [password, setPassword] = useState('demo1234')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (hydrated && token) {
      router.replace('/')
    }
  }, [hydrated, token, router])

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const { data } = await authApi.login(email, password)
      setAuth(data.access_token, data.user)
      toast.success(`Welcome back, ${data.user.full_name ?? data.user.email}`)
      router.replace('/')
    } catch (err: any) {
      const msg = err?.response?.data?.detail ?? 'Login failed'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-dark-950 px-4">
      <div className="w-full max-w-md card">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
            <Zap className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white">AEO Dashboard</h1>
            <p className="text-xs text-dark-400">Sign in to continue</p>
          </div>
        </div>
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="text-sm text-dark-300">Email</label>
            <input
              type="email"
              className="input mt-1"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>
          <div>
            <label className="text-sm text-dark-300">Password</label>
            <input
              type="password"
              className="input mt-1"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>
          <Button type="submit" className="w-full" isLoading={loading}>
            Sign in
          </Button>
          <p className="text-xs text-dark-500 text-center">
            Demo: demo@aeo.local / demo1234
          </p>
        </form>
      </div>
    </div>
  )
}
