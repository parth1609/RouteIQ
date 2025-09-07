import React, { useState, useEffect } from 'react'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { zammadAPI, zendeskAPI, classifierAPI, handleAPIError } from '@/services/api'
import { cn } from '@/lib/utils'

/**
 * Settings Page
 * Configuration and management of integrations and system settings
 */
const SettingsPage = () => {
  const [activeTab, setActiveTab] = useState('integrations')
  const [loading, setLoading] = useState(false)
  const [settings, setSettings] = useState({
    zammad: {
      url: '',
      token: '',
      status: 'disconnected'
    },
    zendesk: {
      subdomain: '',
      email: '',
      token: '',
      status: 'disconnected'
    },
    ai: {
      model: 'default',
      confidence_threshold: 0.8,
      auto_classify: true,
      status: 'active'
    },
    notifications: {
      email_alerts: true,
      slack_integration: false,
      webhook_url: ''
    }
  })

  useEffect(() => {
    loadSettings()
    checkIntegrationStatus()
  }, [])

  const loadSettings = () => {
    // In a real app, this would load from backend/localStorage
    const savedSettings = localStorage.getItem('routeiq_settings')
    if (savedSettings) {
      setSettings(prev => ({ ...prev, ...JSON.parse(savedSettings) }))
    }
  }

  const saveSettings = (newSettings) => {
    setSettings(newSettings)
    localStorage.setItem('routeiq_settings', JSON.stringify(newSettings))
  }

  const checkIntegrationStatus = async () => {
    setLoading(true)
    try {
      // Check Zammad status
      try {
        await zammadAPI.health()
        setSettings(prev => ({
          ...prev,
          zammad: { ...prev.zammad, status: 'connected' }
        }))
      } catch {
        setSettings(prev => ({
          ...prev,
          zammad: { ...prev.zammad, status: 'disconnected' }
        }))
      }

      // Check Zendesk status
      try {
        await zendeskAPI.health()
        setSettings(prev => ({
          ...prev,
          zendesk: { ...prev.zendesk, status: 'connected' }
        }))
      } catch {
        setSettings(prev => ({
          ...prev,
          zendesk: { ...prev.zendesk, status: 'disconnected' }
        }))
      }

      // Check AI Classifier status
      try {
        await classifierAPI.health()
        setSettings(prev => ({
          ...prev,
          ai: { ...prev.ai, status: 'active' }
        }))
      } catch {
        setSettings(prev => ({
          ...prev,
          ai: { ...prev.ai, status: 'inactive' }
        }))
      }
    } catch (error) {
      console.error('Failed to check integration status:', handleAPIError(error))
    } finally {
      setLoading(false)
    }
  }

  const testConnection = async (integration) => {
    setLoading(true)
    try {
      let result
      switch (integration) {
        case 'zammad':
          result = await zammadAPI.health()
          break
        case 'zendesk':
          result = await zendeskAPI.health()
          break
        case 'ai':
          result = await classifierAPI.health()
          break
        default:
          throw new Error('Unknown integration')
      }
      
      setSettings(prev => ({
        ...prev,
        [integration]: { ...prev[integration], status: 'connected' }
      }))
      
      // Show success message (in real app, use toast)
      alert(`${integration} connection successful!`)
    } catch (error) {
      setSettings(prev => ({
        ...prev,
        [integration]: { ...prev[integration], status: 'disconnected' }
      }))
      
      const errorInfo = handleAPIError(error)
      alert(`${integration} connection failed: ${errorInfo.message}`)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'connected':
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'disconnected':
      case 'inactive':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-yellow-100 text-yellow-800'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected':
      case 'active':
        return '✅'
      case 'disconnected':
      case 'inactive':
        return '❌'
      default:
        return '⚠️'
    }
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
            <p className="text-gray-600">Configure integrations and system preferences</p>
          </div>
          
          <Button onClick={checkIntegrationStatus} disabled={loading}>
            {loading ? 'Checking...' : '🔄 Refresh Status'}
          </Button>
        </div>

        {/* Tab Navigation */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('integrations')}
              className={cn(
                "py-2 px-1 border-b-2 font-medium text-sm",
                activeTab === 'integrations'
                  ? "border-brand-end text-brand-end"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              )}
            >
              Integrations
            </button>
            <button
              onClick={() => setActiveTab('ai')}
              className={cn(
                "py-2 px-1 border-b-2 font-medium text-sm",
                activeTab === 'ai'
                  ? "border-brand-end text-brand-end"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              )}
            >
              AI Configuration
            </button>
            <button
              onClick={() => setActiveTab('notifications')}
              className={cn(
                "py-2 px-1 border-b-2 font-medium text-sm",
                activeTab === 'notifications'
                  ? "border-brand-end text-brand-end"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              )}
            >
              Notifications
            </button>
          </nav>
        </div>

        {/* Integrations Tab */}
        {activeTab === 'integrations' && (
          <div className="space-y-6">
            {/* Zammad Integration */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center space-x-2">
                      <span>Zammad Integration</span>
                      <span className={cn(
                        "px-2 py-1 rounded-full text-xs font-medium",
                        getStatusColor(settings.zammad.status)
                      )}>
                        {getStatusIcon(settings.zammad.status)} {settings.zammad.status}
                      </span>
                    </CardTitle>
                    <CardDescription>
                      Connect to your Zammad instance for ticket management
                    </CardDescription>
                  </div>
                  <Button
                    variant="outline"
                    onClick={() => testConnection('zammad')}
                    disabled={loading}
                  >
                    Test Connection
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Zammad URL
                    </label>
                    <input
                      type="url"
                      value={settings.zammad.url}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        zammad: { ...prev.zammad, url: e.target.value }
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-end focus:border-transparent"
                      placeholder="https://your-zammad.com"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      API Token
                    </label>
                    <input
                      type="password"
                      value={settings.zammad.token}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        zammad: { ...prev.zammad, token: e.target.value }
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-end focus:border-transparent"
                      placeholder="Enter API token"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Zendesk Integration */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center space-x-2">
                      <span>Zendesk Integration</span>
                      <span className={cn(
                        "px-2 py-1 rounded-full text-xs font-medium",
                        getStatusColor(settings.zendesk.status)
                      )}>
                        {getStatusIcon(settings.zendesk.status)} {settings.zendesk.status}
                      </span>
                    </CardTitle>
                    <CardDescription>
                      Connect to your Zendesk instance for ticket management
                    </CardDescription>
                  </div>
                  <Button
                    variant="outline"
                    onClick={() => testConnection('zendesk')}
                    disabled={loading}
                  >
                    Test Connection
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Subdomain
                    </label>
                    <input
                      type="text"
                      value={settings.zendesk.subdomain}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        zendesk: { ...prev.zendesk, subdomain: e.target.value }
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-end focus:border-transparent"
                      placeholder="your-company"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email
                    </label>
                    <input
                      type="email"
                      value={settings.zendesk.email}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        zendesk: { ...prev.zendesk, email: e.target.value }
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-end focus:border-transparent"
                      placeholder="admin@company.com"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      API Token
                    </label>
                    <input
                      type="password"
                      value={settings.zendesk.token}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        zendesk: { ...prev.zendesk, token: e.target.value }
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-end focus:border-transparent"
                      placeholder="Enter API token"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Save Button */}
            <div className="flex justify-end">
              <Button onClick={() => saveSettings(settings)}>
                💾 Save Integration Settings
              </Button>
            </div>
          </div>
        )}

        {/* AI Configuration Tab */}
        {activeTab === 'ai' && (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <span>AI Classifier Configuration</span>
                  <span className={cn(
                    "px-2 py-1 rounded-full text-xs font-medium",
                    getStatusColor(settings.ai.status)
                  )}>
                    {getStatusIcon(settings.ai.status)} {settings.ai.status}
                  </span>
                </CardTitle>
                <CardDescription>
                  Configure AI-powered ticket classification settings
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Model Version
                      </label>
                      <select
                        value={settings.ai.model}
                        onChange={(e) => setSettings(prev => ({
                          ...prev,
                          ai: { ...prev.ai, model: e.target.value }
                        }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-end focus:border-transparent"
                      >
                        <option value="default">Default Model (v1.0)</option>
                        <option value="enhanced">Enhanced Model (v2.0)</option>
                        <option value="custom">Custom Model</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Confidence Threshold ({Math.round(settings.ai.confidence_threshold * 100)}%)
                      </label>
                      <input
                        type="range"
                        min="0.5"
                        max="1"
                        step="0.05"
                        value={settings.ai.confidence_threshold}
                        onChange={(e) => setSettings(prev => ({
                          ...prev,
                          ai: { ...prev.ai, confidence_threshold: parseFloat(e.target.value) }
                        }))}
                        className="w-full"
                      />
                      <div className="text-xs text-gray-500 mt-1">
                        Minimum confidence required for automatic classification
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      id="auto_classify"
                      checked={settings.ai.auto_classify}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        ai: { ...prev.ai, auto_classify: e.target.checked }
                      }))}
                      className="rounded border-gray-300 text-brand-end focus:ring-brand-end"
                    />
                    <label htmlFor="auto_classify" className="text-sm font-medium text-gray-700">
                      Enable automatic classification for new tickets
                    </label>
                  </div>
                  
                  <Button
                    variant="outline"
                    onClick={() => testConnection('ai')}
                    disabled={loading}
                  >
                    Test AI Classifier
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Notifications Tab */}
        {activeTab === 'notifications' && (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Notification Preferences</CardTitle>
                <CardDescription>
                  Configure how you receive alerts and updates
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      id="email_alerts"
                      checked={settings.notifications.email_alerts}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        notifications: { ...prev.notifications, email_alerts: e.target.checked }
                      }))}
                      className="rounded border-gray-300 text-brand-end focus:ring-brand-end"
                    />
                    <label htmlFor="email_alerts" className="text-sm font-medium text-gray-700">
                      Enable email alerts for high-priority tickets
                    </label>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      id="slack_integration"
                      checked={settings.notifications.slack_integration}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        notifications: { ...prev.notifications, slack_integration: e.target.checked }
                      }))}
                      className="rounded border-gray-300 text-brand-end focus:ring-brand-end"
                    />
                    <label htmlFor="slack_integration" className="text-sm font-medium text-gray-700">
                      Enable Slack notifications
                    </label>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Webhook URL (Optional)
                    </label>
                    <input
                      type="url"
                      value={settings.notifications.webhook_url}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        notifications: { ...prev.notifications, webhook_url: e.target.value }
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-end focus:border-transparent"
                      placeholder="https://hooks.slack.com/services/..."
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      Webhook URL for custom integrations
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            {/* Save Button */}
            <div className="flex justify-end">
              <Button onClick={() => saveSettings(settings)}>
                💾 Save Notification Settings
              </Button>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}

export { SettingsPage }
