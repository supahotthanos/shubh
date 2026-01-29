import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AEO Dashboard | AI Citation Tracking',
  description: 'Track and optimize your AI visibility across ChatGPT, Perplexity, Claude, and more',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-dark-950 text-white`}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}
