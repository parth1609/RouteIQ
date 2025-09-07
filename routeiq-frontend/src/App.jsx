import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Header } from '@/components/layout/Header'
import { HomePage } from '@/components/pages/HomePage'
import { AboutPage } from '@/components/pages/AboutPage'
import { FeaturesPage } from '@/components/pages/FeaturesPage'
import { ContactPage } from '@/components/pages/ContactPage'
import { DashboardPage } from '@/components/pages/DashboardPage'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={
            <>
              <Header />
              <main><HomePage /></main>
            </>
          } />
          <Route path="/about" element={
            <>
              <Header />
              <main><AboutPage /></main>
            </>
          } />
          <Route path="/features" element={
            <>
              <Header />
              <main><FeaturesPage /></main>
            </>
          } />
          <Route path="/contact" element={
            <>
              <Header />
              <main><ContactPage /></main>
            </>
          } />
          
          {/* Dashboard Routes */}
          <Route path="/dashboard" element={<DashboardPage />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
