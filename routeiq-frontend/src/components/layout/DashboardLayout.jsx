import React, { useState } from 'react'
import { useAuth } from '@/components/auth/AuthContext'
import { cn } from '@/lib/utils'

/**
 * Dashboard Layout Component
 * Provides sidebar navigation and main content area for authenticated users
 */
const DashboardLayout = ({ children, className }) => {
  const { user } = useAuth()
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [isOpen, setIsOpen] = useState(false)

  const navigationItems = [
    { name: 'Dashboard', href: '/dashboard', icon: '📊', active: true },
    { name: 'Tickets', href: '/tickets', icon: '🎫', active: false },
    { name: 'AI Classification', href: '/ai-classification', icon: '🤖', active: false },
    { name: 'Analytics', href: '/analytics', icon: '📈', active: false },
    { name: 'Settings', href: '/settings', icon: '⚙️', active: false },
  ]

  return (
    <div className="min-h-screen bg-page-gradient">
      <div className="flex">
        {/* Sidebar */}
        <div className={cn(
          "fixed inset-y-0 left-0 z-50 w-64 bg-brand-gradient shadow-brand-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}>
          <div className="absolute inset-0 bg-brand-animated opacity-10 animate-gradient-shift" style={{backgroundSize: '400% 400%'}}></div>
          <div className="flex items-center justify-between h-16 px-6 border-b border-white/20 relative z-10">
            <div className="flex items-center">
              <div className="h-10 w-10 rounded-xl bg-white/20 backdrop-blur-sm border border-white/30 flex items-center justify-center shadow-brand">
                <div className="h-6 w-6 rounded-lg bg-gradient-to-r from-white to-white/80"></div>
              </div>
              <span className="ml-3 text-xl font-bold text-white drop-shadow-sm">
                Route<span className="text-white/90">IQ</span>
              </span>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="lg:hidden p-2 rounded-md text-white/80 hover:text-white hover:bg-white/10 transition-colors"
            >
              <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          {/* Navigation */}
          <nav className="mt-8 space-y-2 px-4 relative z-10">
            <a href="/dashboard" className="flex items-center px-4 py-3 text-white/90 hover:text-white hover:bg-white/10 rounded-xl transition-all duration-300 group">
              <span className="mr-3 text-lg group-hover:scale-110 transition-transform">📊</span>
              <span className="font-medium">Dashboard</span>
            </a>
            <a href="/tickets" className="flex items-center px-4 py-3 text-white/90 hover:text-white hover:bg-white/10 rounded-xl transition-all duration-300 group">
              <span className="mr-3 text-lg group-hover:scale-110 transition-transform">🎫</span>
              <span className="font-medium">Tickets</span>
            </a>
            <a href="/ai-classification" className="flex items-center px-4 py-3 text-white/90 hover:text-white hover:bg-white/10 rounded-xl transition-all duration-300 group">
              <span className="mr-3 text-lg group-hover:scale-110 transition-transform">🤖</span>
              <span className="font-medium">AI Classification</span>
            </a>
            <a href="/analytics" className="flex items-center px-4 py-3 text-white/90 hover:text-white hover:bg-white/10 rounded-xl transition-all duration-300 group">
              <span className="mr-3 text-lg group-hover:scale-110 transition-transform">📈</span>
              <span className="font-medium">Analytics</span>
            </a>
            <a href="/settings" className="flex items-center px-4 py-3 text-white/90 hover:text-white hover:bg-white/10 rounded-xl transition-all duration-300 group">
              <span className="mr-3 text-lg group-hover:scale-110 transition-transform">⚙️</span>
              <span className="font-medium">Settings</span>
            </a>
          </nav>

          {/* User Profile */}
          <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-white/20 bg-white/5 backdrop-blur-sm relative z-10">
            <div className="flex items-center space-x-3">
              <div className="h-10 w-10 rounded-full bg-white/20 backdrop-blur-sm border border-white/30 flex items-center justify-center">
                <span className="text-white text-sm font-bold">
                  {user?.name?.charAt(0) || 'U'}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">
                  {user?.name || 'User'}
                </p>
                <p className="text-xs text-white/70 truncate">
                  {user?.email || 'user@example.com'}
                </p>
              </div>
            </div>
          </div>

          {/* Sidebar Toggle */}
          <div className="p-4 border-t">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="flex items-center justify-center w-full px-3 py-2 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-100"
            >
              <span className="text-lg">{sidebarOpen ? '◀' : '▶'}</span>
              {sidebarOpen && <span className="ml-3">Collapse</span>}
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 lg:ml-64">
          <div className="lg:hidden">
            <button
              onClick={() => setIsOpen(true)}
              className="fixed top-4 left-4 z-40 p-2 rounded-md bg-white shadow-lg text-gray-600 hover:text-gray-900"
            >
              <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
          
          <main className={cn("p-6", className)}>
            {children}
          </main>
        </div>

        {/* Mobile overlay */}
        {isOpen && (
          <div
            className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
            onClick={() => setIsOpen(false)}
          />
        )}
      </div>
    </div>
  )
}

export { DashboardLayout }
