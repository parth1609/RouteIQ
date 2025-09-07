import React, { useState, useEffect } from 'react'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { MetricCard } from '@/components/ui/MetricCard'
import { SystemHealthWidget } from '@/components/ui/SystemHealthWidget'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { zammadAPI, zendeskAPI, handleAPIError } from '@/services/api'

/**
 * Dashboard Page Component
 * Main dashboard showing system overview, metrics, and recent activity
 */
const DashboardPage = () => {
  const [metrics, setMetrics] = useState({
    totalTickets: { value: '---', trend: 'neutral', trendValue: '0%' },
    openTickets: { value: '---', trend: 'neutral', trendValue: '0%' },
    resolvedToday: { value: '---', trend: 'up', trendValue: '+12%' },
    avgResolutionTime: { value: '---', trend: 'down', trendValue: '-8%' }
  })

  const [recentTickets, setRecentTickets] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    setLoading(true)
    try {
      // Load recent tickets from Zammad
      const zammadResponse = await zammadAPI.listTickets({ limit: 5 })
      if (zammadResponse.data) {
        setRecentTickets(zammadResponse.data.tickets || [])
      }

      // Simulate metrics (in real app, these would come from analytics API)
      setMetrics({
        totalTickets: { value: '1,247', trend: 'up', trendValue: '+5.2%' },
        openTickets: { value: '89', trend: 'down', trendValue: '-12%' },
        resolvedToday: { value: '34', trend: 'up', trendValue: '+18%' },
        avgResolutionTime: { value: '2.4h', trend: 'down', trendValue: '-15%' }
      })
    } catch (error) {
      console.error('Failed to load dashboard data:', handleAPIError(error))
    } finally {
      setLoading(false)
    }
  }

  const quickActions = [
    { name: 'Create Ticket', icon: '➕', action: () => window.location.href = '/tickets/create' },
    { name: 'View All Tickets', icon: '📋', action: () => window.location.href = '/tickets' },
    { name: 'AI Insights', icon: '🤖', action: () => window.location.href = '/ai' },
    { name: 'Analytics', icon: '📊', action: () => window.location.href = '/analytics' }
  ]

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Metrics Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="Total Tickets"
            value={metrics.totalTickets.value}
            description="All time tickets created"
            icon="🎫"
            trend={metrics.totalTickets.trend}
            trendValue={metrics.totalTickets.trendValue}
          />
          <MetricCard
            title="Open Tickets"
            value={metrics.openTickets.value}
            description="Currently unresolved"
            icon="🔓"
            trend={metrics.openTickets.trend}
            trendValue={metrics.openTickets.trendValue}
          />
          <MetricCard
            title="Resolved Today"
            value={metrics.resolvedToday.value}
            description="Tickets closed today"
            icon="✅"
            trend={metrics.resolvedToday.trend}
            trendValue={metrics.resolvedToday.trendValue}
          />
          <MetricCard
            title="Avg Resolution Time"
            value={metrics.avgResolutionTime.value}
            description="Average time to resolve"
            icon="⏱️"
            trend={metrics.avgResolutionTime.trend}
            trendValue={metrics.avgResolutionTime.trendValue}
          />
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* System Health */}
          <div className="lg:col-span-1">
            <SystemHealthWidget />
          </div>

          {/* Recent Activity */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <span className="text-lg mr-2">📋</span>
                  Recent Tickets
                </CardTitle>
                <CardDescription>
                  Latest ticket activity across all platforms
                </CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="space-y-3">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="animate-pulse">
                        <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                        <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                      </div>
                    ))}
                  </div>
                ) : recentTickets.length > 0 ? (
                  <div className="space-y-3">
                    {recentTickets.slice(0, 5).map((ticket) => (
                      <div key={ticket.id} className="flex items-center justify-between p-3 rounded-lg border hover:bg-gray-50">
                        <div className="flex-1">
                          <div className="font-medium text-gray-900">
                            #{ticket.id} - {ticket.title || ticket.subject}
                          </div>
                          <div className="text-sm text-gray-500">
                            {ticket.customer || 'Unknown Customer'} • {ticket.created_at ? new Date(ticket.created_at).toLocaleDateString() : 'Unknown Date'}
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            ticket.state === 'open' ? 'bg-yellow-100 text-yellow-800' :
                            ticket.state === 'closed' ? 'bg-green-100 text-green-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {ticket.state || 'unknown'}
                          </span>
                          <span className="text-xs text-gray-400">Zammad</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <div className="text-4xl mb-2">📭</div>
                    <div>No recent tickets found</div>
                  </div>
                )}
                <div className="mt-4 pt-4 border-t">
                  <Button variant="outline" className="w-full">
                    View All Tickets
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <span className="text-lg mr-2">⚡</span>
              Quick Actions
            </CardTitle>
            <CardDescription>
              Common tasks and shortcuts
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {quickActions.map((action) => (
                <Button
                  key={action.name}
                  variant="outline"
                  className="h-20 flex flex-col items-center justify-center space-y-2"
                  onClick={action.action}
                >
                  <span className="text-2xl">{action.icon}</span>
                  <span className="text-sm">{action.name}</span>
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* AI Classification Insights */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <span className="text-lg mr-2">🤖</span>
              AI Classification Insights
            </CardTitle>
            <CardDescription>
              Recent AI-powered ticket classification performance
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold brand-text mb-2">94.2%</div>
                <div className="text-sm text-gray-600">Classification Accuracy</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold brand-text mb-2">156</div>
                <div className="text-sm text-gray-600">Tickets Classified Today</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold brand-text mb-2">1.2s</div>
                <div className="text-sm text-gray-600">Avg Classification Time</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}

export { DashboardPage }
