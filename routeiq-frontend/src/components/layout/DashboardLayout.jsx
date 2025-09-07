import React, { useState } from 'react'
import { cn } from '@/lib/utils'

/**
 * Dashboard Layout Component
 * Provides sidebar navigation and main content area for authenticated users
 */
const DashboardLayout = ({ children, className }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const navigationItems = [
    { name: 'Dashboard', href: '/dashboard', icon: '📊', active: true },
    { name: 'Tickets', href: '/tickets', icon: '🎫', active: false },
    { name: 'AI Classification', href: '/ai', icon: '🤖', active: false },
    { name: 'Analytics', href: '/analytics', icon: '📈', active: false },
    { name: 'Settings', href: '/settings', icon: '⚙️', active: false },
  ]

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={cn(
        "bg-white shadow-sm border-r transition-all duration-300",
        sidebarOpen ? "w-64" : "w-16"
      )}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center px-4 py-6 border-b">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-r from-brand-start via-brand-mid to-brand-end"></div>
            {sidebarOpen && (
              <span className="ml-3 text-xl font-bold text-gray-900">
                Route<span className="brand-text">IQ</span>
              </span>
            )}
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navigationItems.map((item) => (
              <a
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                  item.active
                    ? "bg-brand-end/10 text-brand-end"
                    : "text-gray-700 hover:bg-gray-100"
                )}
              >
                <span className="text-lg">{item.icon}</span>
                {sidebarOpen && <span className="ml-3">{item.name}</span>}
              </a>
            ))}
          </nav>

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
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <header className="bg-white shadow-sm border-b px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <div className="flex items-center space-x-4">
              <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100">
                🔔
              </button>
              <div className="h-8 w-8 bg-gray-300 rounded-full"></div>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <main className={cn("flex-1 overflow-auto p-6", className)}>
          {children}
        </main>
      </div>
    </div>
  )
}

export { DashboardLayout }
