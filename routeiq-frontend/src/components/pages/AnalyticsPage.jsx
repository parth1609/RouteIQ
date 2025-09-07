import React, { useState, useEffect } from 'react'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { zammadAPI, zendeskAPI, classifierAPI, handleAPIError } from '@/services/api'
import { cn } from '@/lib/utils'

/**
 * Analytics Page
 * Comprehensive analytics dashboard with charts and insights
 */
const AnalyticsPage = () => {
  const [timeRange, setTimeRange] = useState('7d')
  const [loading, setLoading] = useState(false)
  const [analytics, setAnalytics] = useState({
    overview: {
      totalTickets: 0,
      openTickets: 0,
      resolvedTickets: 0,
      avgResolutionTime: 0,
      customerSatisfaction: 0
    },
    trends: {
      ticketVolume: [],
      resolutionTimes: [],
      priorityBreakdown: {}
    },
    performance: {
      agentStats: [],
      departmentStats: [],
      platformComparison: {}
    },
    aiInsights: {
      accuracy: 0,
      predictions: 0,
      topCategories: []
    }
  })

  useEffect(() => {
    loadAnalytics()
  }, [timeRange])

  const loadAnalytics = async () => {
    setLoading(true)
    try {
      // In a real implementation, this would call actual analytics endpoints
      // For now, we'll generate mock data based on the time range
      const mockData = generateMockAnalytics(timeRange)
      setAnalytics(mockData)
    } catch (error) {
      console.error('Failed to load analytics:', handleAPIError(error))
    } finally {
      setLoading(false)
    }
  }

  const generateMockAnalytics = (range) => {
    const days = range === '7d' ? 7 : range === '30d' ? 30 : 90
    const multiplier = days / 7

    return {
      overview: {
        totalTickets: Math.floor(156 * multiplier),
        openTickets: Math.floor(23 * multiplier),
        resolvedTickets: Math.floor(133 * multiplier),
        avgResolutionTime: 4.2 + (Math.random() * 2 - 1),
        customerSatisfaction: 4.3 + (Math.random() * 0.4 - 0.2)
      },
      trends: {
        ticketVolume: Array.from({ length: days }, (_, i) => ({
          date: new Date(Date.now() - (days - i - 1) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          tickets: Math.floor(Math.random() * 25) + 5
        })),
        priorityBreakdown: {
          high: Math.floor(Math.random() * 15) + 10,
          medium: Math.floor(Math.random() * 20) + 40,
          low: Math.floor(Math.random() * 15) + 35
        }
      },
      performance: {
        platformComparison: {
          zammad: {
            tickets: Math.floor(89 * multiplier),
            avgResolution: 3.8,
            satisfaction: 4.4
          },
          zendesk: {
            tickets: Math.floor(67 * multiplier),
            avgResolution: 4.6,
            satisfaction: 4.2
          }
        },
        departmentStats: [
          { name: 'IT Support', tickets: Math.floor(45 * multiplier), avgTime: 3.2 },
          { name: 'Network', tickets: Math.floor(32 * multiplier), avgTime: 5.1 },
          { name: 'Security', tickets: Math.floor(28 * multiplier), avgTime: 6.3 },
          { name: 'Hardware', tickets: Math.floor(21 * multiplier), avgTime: 4.8 }
        ]
      },
      aiInsights: {
        accuracy: 0.942 + (Math.random() * 0.02 - 0.01),
        predictions: Math.floor(234 * multiplier),
        topCategories: [
          { category: 'Email Issues', count: Math.floor(45 * multiplier) },
          { category: 'Network Problems', count: Math.floor(38 * multiplier) },
          { category: 'Software Bugs', count: Math.floor(32 * multiplier) },
          { category: 'Hardware Failures', count: Math.floor(28 * multiplier) }
        ]
      }
    }
  }

  const timeRangeOptions = [
    { value: '7d', label: 'Last 7 days' },
    { value: '30d', label: 'Last 30 days' },
    { value: '90d', label: 'Last 90 days' }
  ]

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
            <p className="text-gray-600">Comprehensive insights and performance metrics</p>
          </div>
          
          <div className="flex items-center space-x-4">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-end focus:border-transparent"
            >
              {timeRangeOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            
            <Button onClick={loadAnalytics} disabled={loading}>
              {loading ? 'Loading...' : '🔄 Refresh'}
            </Button>
          </div>
        </div>

        {/* Overview Metrics */}
        <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-6">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Total Tickets</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold brand-text">
                {analytics.overview.totalTickets.toLocaleString()}
              </div>
              <p className="text-xs text-gray-500 mt-1">
                +12% from previous period
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Open Tickets</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-yellow-600">
                {analytics.overview.openTickets}
              </div>
              <p className="text-xs text-gray-500 mt-1">
                -5% from previous period
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Resolved</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">
                {analytics.overview.resolvedTickets}
              </div>
              <p className="text-xs text-gray-500 mt-1">
                +18% from previous period
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Avg Resolution</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">
                {analytics.overview.avgResolutionTime.toFixed(1)}h
              </div>
              <p className="text-xs text-gray-500 mt-1">
                -8% from previous period
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Satisfaction</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-purple-600">
                {analytics.overview.customerSatisfaction.toFixed(1)}/5
              </div>
              <p className="text-xs text-gray-500 mt-1">
                +3% from previous period
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Charts Row */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Ticket Volume Trend */}
          <Card>
            <CardHeader>
              <CardTitle>Ticket Volume Trend</CardTitle>
              <CardDescription>Daily ticket creation over time</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-end justify-between space-x-1">
                {analytics.trends.ticketVolume.slice(-14).map((day, index) => (
                  <div key={index} className="flex flex-col items-center flex-1">
                    <div
                      className="w-full bg-brand-end rounded-t"
                      style={{
                        height: `${(day.tickets / Math.max(...analytics.trends.ticketVolume.map(d => d.tickets))) * 200}px`,
                        minHeight: '4px'
                      }}
                    ></div>
                    <div className="text-xs text-gray-500 mt-2 transform -rotate-45 origin-left">
                      {new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Priority Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle>Priority Distribution</CardTitle>
              <CardDescription>Tickets by priority level</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Object.entries(analytics.trends.priorityBreakdown).map(([priority, percentage]) => (
                  <div key={priority} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={cn(
                        "w-4 h-4 rounded-full",
                        priority === 'high' ? 'bg-red-500' :
                        priority === 'medium' ? 'bg-yellow-500' :
                        'bg-green-500'
                      )}></div>
                      <span className="capitalize font-medium">{priority} Priority</span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <div className="w-32 bg-gray-200 rounded-full h-3">
                        <div 
                          className={cn(
                            "h-3 rounded-full",
                            priority === 'high' ? 'bg-red-500' :
                            priority === 'medium' ? 'bg-yellow-500' :
                            'bg-green-500'
                          )}
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium w-12 text-right">{percentage}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Performance Analytics */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Platform Comparison */}
          <Card>
            <CardHeader>
              <CardTitle>Platform Performance</CardTitle>
              <CardDescription>Zammad vs Zendesk comparison</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {Object.entries(analytics.performance.platformComparison).map(([platform, stats]) => (
                  <div key={platform} className="space-y-3">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium capitalize">{platform}</h4>
                      <span className={cn(
                        "px-2 py-1 rounded-full text-xs font-medium",
                        platform === 'zammad' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'
                      )}>
                        {stats.tickets} tickets
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Avg Resolution:</span>
                        <span className="ml-2 font-medium">{stats.avgResolution}h</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Satisfaction:</span>
                        <span className="ml-2 font-medium">{stats.satisfaction}/5</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Department Performance */}
          <Card>
            <CardHeader>
              <CardTitle>Department Performance</CardTitle>
              <CardDescription>Performance metrics by department</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analytics.performance.departmentStats.map((dept, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <div className="font-medium">{dept.name}</div>
                      <div className="text-sm text-gray-600">{dept.tickets} tickets</div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">{dept.avgTime}h</div>
                      <div className="text-sm text-gray-600">avg time</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* AI Insights */}
        <Card>
          <CardHeader>
            <CardTitle>AI Classification Insights</CardTitle>
            <CardDescription>Performance and usage of AI-powered classification</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold brand-text mb-2">
                  {Math.round(analytics.aiInsights.accuracy * 100)}%
                </div>
                <div className="text-sm font-medium text-gray-600">Classification Accuracy</div>
                <div className="text-xs text-gray-500 mt-1">+2.1% this period</div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold brand-text mb-2">
                  {analytics.aiInsights.predictions.toLocaleString()}
                </div>
                <div className="text-sm font-medium text-gray-600">AI Predictions</div>
                <div className="text-xs text-gray-500 mt-1">+15% this period</div>
              </div>
              
              <div>
                <div className="text-sm font-medium text-gray-600 mb-3">Top Categories</div>
                <div className="space-y-2">
                  {analytics.aiInsights.topCategories.slice(0, 4).map((cat, index) => (
                    <div key={index} className="flex items-center justify-between text-sm">
                      <span>{cat.category}</span>
                      <span className="font-medium">{cat.count}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}

export { AnalyticsPage }
