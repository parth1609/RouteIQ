import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { healthAPI, handleAPIError } from '@/services/api'
import { cn } from '@/lib/utils'

/**
 * System Health Widget Component
 * Displays real-time health status of all integrated services with vibrant gradient styling
 */
const SystemHealthWidget = ({ className }) => {
  const [healthStatus, setHealthStatus] = useState({
    api: { status: 'loading', message: 'Checking...' },
    classifier: { status: 'loading', message: 'Checking...' },
    zendesk: { status: 'loading', message: 'Checking...' },
    zammad: { status: 'loading', message: 'Checking...' }
  })

  const checkHealth = async () => {
    const checks = [
      { key: 'api', name: 'API Gateway', check: healthAPI.checkAPI },
      { key: 'classifier', name: 'AI Classifier', check: healthAPI.checkClassifier },
      { key: 'zendesk', name: 'Zendesk', check: healthAPI.checkZendesk },
      { key: 'zammad', name: 'Zammad', check: healthAPI.checkZammad }
    ]

    for (const { key, name, check } of checks) {
      try {
        await check()
        setHealthStatus(prev => ({
          ...prev,
          [key]: { status: 'healthy', message: 'Online' }
        }))
      } catch (error) {
        const errorInfo = handleAPIError(error)
        setHealthStatus(prev => ({
          ...prev,
          [key]: { status: 'error', message: errorInfo.message }
        }))
      }
    }
  }

  useEffect(() => {
    checkHealth()
    const interval = setInterval(checkHealth, 30000) // Check every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'text-success-700 bg-success-gradient border-success-200 shadow-success'
      case 'error': return 'text-error-700 bg-error-gradient border-error-200 shadow-error'
      case 'loading': return 'text-warning-700 bg-warning-gradient border-warning-200 shadow-warning animate-pulse'
      default: return 'text-gray-700 bg-gray-gradient border-gray-200 shadow-sm'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy': return '🟢'
      case 'error': return '🔴'
      case 'loading': return '🟡'
      default: return '⚪'
    }
  }

  const getServiceIcon = (key) => {
    switch (key) {
      case 'api': return '🚀'
      case 'classifier': return '🤖'
      case 'zendesk': return '🎫'
      case 'zammad': return '📋'
      default: return '⚙️'
    }
  }

  const getServiceGradient = (key) => {
    switch (key) {
      case 'api': return 'bg-brand-gradient'
      case 'classifier': return 'bg-info-gradient'
      case 'zendesk': return 'bg-success-gradient'
      case 'zammad': return 'bg-warning-gradient'
      default: return 'bg-gray-gradient'
    }
  }

  const services = [
    { key: 'api', name: 'API Gateway', description: 'Core backend services' },
    { key: 'classifier', name: 'AI Classifier', description: 'Machine learning engine' },
    { key: 'zendesk', name: 'Zendesk', description: 'Zendesk integration' },
    { key: 'zammad', name: 'Zammad', description: 'Zammad integration' }
  ]

  return (
    <Card className={cn("bg-white border-0 shadow-brand-lg hover:shadow-brand-xl transition-all duration-300 group", className)}>
      {/* Animated gradient border */}
      <div className="absolute inset-0 bg-brand-animated opacity-10 rounded-lg animate-gradient-shift group-hover:opacity-20 transition-opacity duration-300" style={{backgroundSize: '400% 400%'}} />
      
      <CardHeader className="relative z-10">
        <CardTitle className="flex items-center text-gradient-brand">
          <div className="p-2 rounded-xl bg-brand-gradient mr-3 shadow-brand">
            <span className="text-lg text-white">🏥</span>
          </div>
          System Health
        </CardTitle>
        <CardDescription className="text-gray-600">
          Real-time status of all integrated services
        </CardDescription>
      </CardHeader>
      <CardContent className="relative z-10">
        <div className="space-y-4">
          {services.map((service) => {
            const status = healthStatus[service.key]
            return (
              <div key={service.key} className="relative overflow-hidden rounded-xl border border-gray-100 bg-white hover:shadow-lg transition-all duration-300 group/item">
                {/* Service gradient accent */}
                <div className={cn(
                  "absolute left-0 top-0 bottom-0 w-1 transition-all duration-300 group-hover/item:w-2",
                  getServiceGradient(service.key)
                )} />
                
                <div className="flex items-center justify-between p-4 pl-6">
                  <div className="flex items-center space-x-4">
                    {/* Service icon */}
                    <div className={cn(
                      "p-3 rounded-xl text-white shadow-lg transition-all duration-300 group-hover/item:scale-110",
                      getServiceGradient(service.key)
                    )}>
                      <span className="text-lg">{getServiceIcon(service.key)}</span>
                    </div>
                    
                    {/* Service info */}
                    <div>
                      <div className="font-semibold text-gray-900 group-hover/item:text-brand-600 transition-colors">
                        {service.name}
                      </div>
                      <div className="text-sm text-gray-500">{service.description}</div>
                    </div>
                  </div>
                  
                  {/* Status indicator */}
                  <div className="flex items-center space-x-3">
                    <div className={cn(
                      "px-4 py-2 rounded-full text-xs font-semibold text-white border-0 transition-all duration-300 hover:scale-105",
                      getStatusColor(status.status)
                    )}>
                      {status.message}
                    </div>
                    <div className="text-2xl animate-pulse">
                      {getStatusIcon(status.status)}
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
        
        {/* Refresh button with gradient */}
        <button
          onClick={checkHealth}
          className="mt-6 w-full px-4 py-3 text-sm font-semibold text-white bg-brand-gradient rounded-xl hover:shadow-brand-lg hover:scale-105 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2"
        >
          <span className="flex items-center justify-center space-x-2">
            <span>🔄</span>
            <span>Refresh Status</span>
          </span>
        </button>
      </CardContent>
    </Card>
  )
}

export { SystemHealthWidget }
