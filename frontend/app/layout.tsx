import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'CampusIQ - AI Student Success Platform',
  description: 'AI-powered platform for student success and retention',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <nav className="bg-slate-900 text-white p-4">
          <div className="max-w-7xl mx-auto flex justify-between items-center">
            <a href="/" className="text-xl font-bold">CampusIQ</a>
            <div className="space-x-4">
              <a href="/dashboard" className="hover:text-blue-300">Dashboard</a>
              <a href="/advisor" className="hover:text-blue-300">AI Advisor</a>
              <a href="/students" className="hover:text-blue-300">Students</a>
            </div>
          </div>
        </nav>
        {children}
      </body>
    </html>
  )
}
