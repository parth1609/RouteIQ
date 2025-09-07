import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { AuthProvider } from '@/components/auth/AuthContext'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import { ErrorBoundary } from '@/components/common/ErrorBoundary'
import { Header } from '@/components/layout/Header'
import { HomePage } from '@/components/pages/HomePage'
import { AboutPage } from '@/components/pages/AboutPage'
import { FeaturesPage } from '@/components/pages/FeaturesPage'
import { ContactPage } from '@/components/pages/ContactPage'
import { DashboardPage } from '@/components/pages/DashboardPage'
import { TicketManagementPage } from '@/components/pages/TicketManagementPage'
import { AIClassificationPage } from '@/components/pages/AIClassificationPage'
import { AnalyticsPage } from '@/components/pages/AnalyticsPage'
import { SettingsPage } from '@/components/pages/SettingsPage'

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <div className="min-h-screen bg-gray-50">
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={
                <>
                  <Header />
                  <main>
                    <HomePage />
                  </main>
                </>
              } />
              <Route path="/about" element={
                <>
                  <Header />
                  <main>
                    <AboutPage />
                  </main>
                </>
              } />
              <Route path="/features" element={
                <>
                  <Header />
                  <main>
                    <FeaturesPage />
                  </main>
                </>
              } />
              <Route path="/contact" element={
                <>
                  <Header />
                  <main>
                    <ContactPage />
                  </main>
                </>
              } />
              
              {/* Protected Dashboard Routes */}
              <Route path="/dashboard" element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              } />
              <Route path="/tickets" element={
                <ProtectedRoute>
                  <TicketManagementPage />
                </ProtectedRoute>
              } />
              <Route path="/ai-classification" element={
                <ProtectedRoute>
                  <AIClassificationPage />
                </ProtectedRoute>
              } />
              <Route path="/analytics" element={
                <ProtectedRoute>
                  <AnalyticsPage />
                </ProtectedRoute>
              } />
              <Route path="/settings" element={
                <ProtectedRoute>
                  <SettingsPage />
                </ProtectedRoute>
              } />
            </Routes>
          </div>
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  )
}

export default App
