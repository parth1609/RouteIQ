import React, { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { useAuth } from '@/components/auth/AuthContext'
import { cn } from '@/lib/utils'

/**
 * Header component with RouteIQ branding and navigation
 * Features logo, navigation links, and user menu
 */
export const Header = () => {
  const { user, isAuthenticated, logout } = useAuth()
  const [showUserMenu, setShowUserMenu] = useState(false)

  const handleLogout = () => {
    logout()
    setShowUserMenu(false)
    window.location.href = '/'
  }

  return (
    <header className="bg-brand-gradient shadow-brand border-b-0 relative overflow-visible">
      <div className="absolute inset-0 bg-brand-animated opacity-20 animate-gradient-shift pointer-events-none" style={{backgroundSize: '400% 400%'}}></div>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <div className="h-10 w-10 rounded-xl bg-white/20 backdrop-blur-sm border border-white/30 flex items-center justify-center shadow-brand">
              <div className="h-6 w-6 rounded-lg bg-gradient-to-r from-white to-white/80"></div>
            </div>
            <span className="ml-3 text-xl font-bold text-white drop-shadow-sm">
              Route<span className="text-white/90">IQ</span>
            </span>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex space-x-8">
            <a href="/" className="text-white/90 hover:text-white font-medium transition-all duration-300 hover:drop-shadow-md relative group">
              Home
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-white/80 group-hover:w-full transition-all duration-300"></span>
            </a>
            <a href="/about" className="text-white/90 hover:text-white font-medium transition-all duration-300 hover:drop-shadow-md relative group">
              About
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-white/80 group-hover:w-full transition-all duration-300"></span>
            </a>
            <a href="/features" className="text-white/90 hover:text-white font-medium transition-all duration-300 hover:drop-shadow-md relative group">
              Features
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-white/80 group-hover:w-full transition-all duration-300"></span>
            </a>
            <a href="/contact" className="text-white/90 hover:text-white font-medium transition-all duration-300 hover:drop-shadow-md relative group">
              Contact
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-white/80 group-hover:w-full transition-all duration-300"></span>
            </a>
          </nav>

          {/* Actions */}
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <div className="relative">
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center space-x-3 text-white/90 hover:text-white transition-all duration-300"
                >
                  <div className="h-10 w-10 rounded-full bg-white/20 backdrop-blur-sm border border-white/30 flex items-center justify-center shadow-brand animate-pulse-brand">
                    <span className="text-white text-sm font-bold drop-shadow-sm">
                      {(user?.name?.charAt(0) || 'U')?.toUpperCase()}
                    </span>
                  </div>
                  <span className="hidden lg:block font-medium drop-shadow-sm">{user?.name || 'User'}</span>
                  <svg className="h-4 w-4 drop-shadow-sm" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                {showUserMenu && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border py-1 z-50">
                    <div className="px-4 py-2 border-b">
                      <div className="text-sm font-medium text-gray-900">{user?.name}</div>
                      <div className="text-xs text-gray-500">{user?.email}</div>
                    </div>
                    <a
                      href="/dashboard"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      onClick={() => setShowUserMenu(false)}
                    >
                      Dashboard
                    </a>
                    <a
                      href="/settings"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      onClick={() => setShowUserMenu(false)}
                    >
                      Settings
                    </a>
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center space-x-4">
                <a
                  href="/login"
                  className="text-white/90 hover:text-white font-medium transition-all duration-300 drop-shadow-sm"
                >
                  Sign In
                </a>
                <a
                  href="/login"
                  className="bg-white/20 backdrop-blur-sm border border-white/30 text-white px-6 py-2 rounded-xl font-medium hover:bg-white/30 transition-all duration-300 shadow-brand"
                >
                  Get Started
                </a>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
