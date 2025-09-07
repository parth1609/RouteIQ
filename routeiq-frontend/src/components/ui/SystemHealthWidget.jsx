import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { healthAPI, handleAPIError } from '@/services/api'
import { cn } from '@/lib/utils'

/**
 * System Health Widget Component
 * Displays real-time health status of all integrated services
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
      case 'healthy': return 'text-green-600 bg-green-100'
      case 'error': return 'text-red-600 bg-red-100'
      case 'loading': return 'text-yellow-600 bg-yellow-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy': return '✅'
      case 'error': return '❌'
      case 'loading': return '⏳'
      default: return '❓'
    }
  }

  const services = [
    { key: 'api', name: 'API Gateway', description: 'Core backend services' },
    { key: 'classifier', name: 'AI Classifier', description: 'Machine learning engine' },
    { key: 'zendesk', name: 'Zendesk', description: 'Zendesk integration' },
    { key: 'zammad', name: 'Zammad', description: 'Zammad integration' }
  ]

  return (
    <Card className={cn("", className)}>
      <CardHeader>
        <CardTitle className="flex items-center">
          <span className="text-lg mr-2">🏥</span>
          System Health
        </CardTitle>
        <CardDescription>
          Real-time status of all integrated services
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {services.map((service) => {
            const status = healthStatus[service.key]
            return (
              <div key={service.key} className="flex items-center justify-between p-3 rounded-lg border">
                <div className="flex items-center space-x-3">
                  <span className="text-xl">{getStatusIcon(status.status)}</span>
                  <div>
                    <div className="font-medium text-gray-900">{service.name}</div>
                    <div className="text-sm text-gray-500">{service.description}</div>
                  </div>
                </div>
                <div className={cn(
                  "px-2 py-1 rounded-full text-xs font-medium",
                  getStatusColor(status.status)
                )}>
                  {status.message}
                </div>
              </div>
            )
          })}
        </div>
        <button
          onClick={checkHealth}
          className="mt-4 w-full px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
        >
          Refresh Status
        </button>
      </CardContent>
    </Card>
  )
}

export { SystemHealthWidget }
