import React from 'react'
import { Button } from '@/components/ui/Button'
import { cn } from '@/lib/utils'

/**
 * Header component with RouteIQ branding and navigation
 * Features logo, navigation links, and user menu
 */
const Header = ({ className }) => {
  return (
    <header className={cn(
      "sticky top-0 z-50 w-full border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60",
      className
    )}>
      <div className="container flex h-16 items-center justify-between px-4">
        {/* Logo and Brand */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-r from-brand-start via-brand-mid to-brand-end"></div>
            <span className="text-xl font-bold text-gray-900">
              Route<span className="brand-text">IQ</span>
            </span>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center space-x-6">
          <a href="/" className="text-sm font-medium text-gray-700 hover:text-brand-end transition-colors">
            Home
          </a>
          <a href="/features" className="text-sm font-medium text-gray-700 hover:text-brand-end transition-colors">
            Features
          </a>
          <a href="/about" className="text-sm font-medium text-gray-700 hover:text-brand-end transition-colors">
            About
          </a>
          <a href="/contact" className="text-sm font-medium text-gray-700 hover:text-brand-end transition-colors">
            Contact
          </a>
        </nav>

        {/* Action Buttons */}
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="sm">
            Sign In
          </Button>
          <Button size="sm">
            Get Started
          </Button>
        </div>
      </div>
    </header>
  )
}

export { Header }
