import React from 'react'
import { useAuth } from './AuthContext'
import { LoginPage } from './LoginPage'

/**
 * Protected Route Component
 * Renders children only if user is authenticated, otherwise shows login page
 */
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="h-12 w-12 rounded-lg bg-gradient-to-r from-brand-start via-brand-mid to-brand-end mx-auto mb-4 animate-pulse"></div>
          <div className="text-lg font-medium text-gray-900">Loading...</div>
          <div className="text-sm text-gray-600">Checking authentication</div>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <LoginPage />
  }

  return children
}

export { ProtectedRoute }
