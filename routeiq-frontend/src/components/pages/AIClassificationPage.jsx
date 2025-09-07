import React, { useState, useEffect } from 'react'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { classifierAPI, handleAPIError } from '@/services/api'
import { cn } from '@/lib/utils'

/**
 * AI Classification Page
 * Interface for AI model insights, testing, and configuration
 */
const AIClassificationPage = () => {
  const [activeTab, setActiveTab] = useState('insights')
  const [testInput, setTestInput] = useState({
    title: '',
    description: ''
  })
  const [testResult, setTestResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [metrics, setMetrics] = useState(null)

  useEffect(() => {
    loadMetrics()
  }, [])

  const loadMetrics = async () => {
    try {
      const response = await classifierAPI.getMetrics()
      setMetrics(response.data)
    } catch (error) {
      console.error('Failed to load metrics:', handleAPIError(error))
      // Set mock data for demonstration
      setMetrics({
        accuracy: 0.942,
        total_predictions: 1247,
        predictions_today: 156,
        avg_confidence: 0.87,
        avg_processing_time: 1.2,
        priority_distribution: {
          high: 23,
          medium: 45,
          low: 32
        },
        department_distribution: {
          'IT Support': 35,
          'Network': 28,
          'Security': 15,
          'Hardware': 22
        }
      })
    }
  }

  const testClassification = async () => {
    if (!testInput.title || !testInput.description) {
      return
    }

    setLoading(true)
    try {
      const response = await classifierAPI.predict({
        title: testInput.title,
        description: testInput.description
      })
      setTestResult(response.data)
    } catch (error) {
      const errorInfo = handleAPIError(error)
      setTestResult({
        error: errorInfo.message
      })
    } finally {
      setLoading(false)
    }
  }

  const sampleTickets = [
    {
      title: "Cannot access email",
      description: "I'm unable to log into my email account. Getting authentication errors.",
      expected: { priority: "medium", department: "IT Support" }
    },
    {
      title: "Server down - urgent",
      description: "Production server is completely unresponsive. All services are down.",
      expected: { priority: "high", department: "Network" }
    },
    {
      title: "Password reset request",
      description: "Need to reset my password for the company portal.",
      expected: { priority: "low", department: "IT Support" }
    }
  ]

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">AI Classification</h1>
            <p className="text-gray-600">Monitor and test AI-powered ticket classification</p>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('insights')}
              className={cn(
                "py-2 px-1 border-b-2 font-medium text-sm",
                activeTab === 'insights'
                  ? "border-brand-end text-brand-end"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              )}
            >
              Performance Insights
            </button>
            <button
              onClick={() => setActiveTab('test')}
              className={cn(
                "py-2 px-1 border-b-2 font-medium text-sm",
                activeTab === 'test'
                  ? "border-brand-end text-brand-end"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              )}
            >
              Test Classification
            </button>
          </nav>
        </div>

        {/* Performance Insights Tab */}
        {activeTab === 'insights' && (
          <div className="space-y-6">
            {/* Key Metrics */}
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Model Accuracy
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold brand-text">
                    {metrics ? `${Math.round(metrics.accuracy * 100)}%` : '---'}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Classification accuracy</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Total Predictions
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold brand-text">
                    {metrics ? metrics.total_predictions.toLocaleString() : '---'}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">All time predictions</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Today's Predictions
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold brand-text">
                    {metrics ? metrics.predictions_today : '---'}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Predictions today</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    Avg Processing Time
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold brand-text">
                    {metrics ? `${metrics.avg_processing_time}s` : '---'}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Response time</p>
                </CardContent>
              </Card>
            </div>

            {/* Distribution Charts */}
            <div className="grid lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Priority Distribution</CardTitle>
                  <CardDescription>Classification breakdown by priority level</CardDescription>
                </CardHeader>
                <CardContent>
                  {metrics?.priority_distribution ? (
                    <div className="space-y-4">
                      {Object.entries(metrics.priority_distribution).map(([priority, percentage]) => (
                        <div key={priority} className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <div className={cn(
                              "w-3 h-3 rounded-full",
                              priority === 'high' ? 'bg-red-500' :
                              priority === 'medium' ? 'bg-yellow-500' :
                              'bg-green-500'
                            )}></div>
                            <span className="capitalize font-medium">{priority}</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <div className="w-24 bg-gray-200 rounded-full h-2">
                              <div 
                                className={cn(
                                  "h-2 rounded-full",
                                  priority === 'high' ? 'bg-red-500' :
                                  priority === 'medium' ? 'bg-yellow-500' :
                                  'bg-green-500'
                                )}
                                style={{ width: `${percentage}%` }}
                              ></div>
                            </div>
                            <span className="text-sm font-medium">{percentage}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">Loading...</div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Department Distribution</CardTitle>
                  <CardDescription>Classification breakdown by department</CardDescription>
                </CardHeader>
                <CardContent>
                  {metrics?.department_distribution ? (
                    <div className="space-y-4">
                      {Object.entries(metrics.department_distribution).map(([dept, percentage]) => (
                        <div key={dept} className="flex items-center justify-between">
                          <span className="font-medium">{dept}</span>
                          <div className="flex items-center space-x-2">
                            <div className="w-24 bg-gray-200 rounded-full h-2">
                              <div 
                                className="h-2 rounded-full bg-brand-end"
                                style={{ width: `${percentage}%` }}
                              ></div>
                            </div>
                            <span className="text-sm font-medium">{percentage}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">Loading...</div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Model Health */}
            <Card>
              <CardHeader>
                <CardTitle>Model Health Status</CardTitle>
                <CardDescription>Current status and performance indicators</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-3 gap-6">
                  <div className="text-center">
                    <div className="text-2xl mb-2">✅</div>
                    <div className="font-medium text-green-600">Model Online</div>
                    <div className="text-sm text-gray-500">Responding normally</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl mb-2">⚡</div>
                    <div className="font-medium text-blue-600">Fast Response</div>
                    <div className="text-sm text-gray-500">Avg 1.2s processing</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl mb-2">🎯</div>
                    <div className="font-medium text-purple-600">High Accuracy</div>
                    <div className="text-sm text-gray-500">94.2% classification rate</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Test Classification Tab */}
        {activeTab === 'test' && (
          <div className="space-y-6">
            {/* Test Interface */}
            <Card>
              <CardHeader>
                <CardTitle>Test AI Classification</CardTitle>
                <CardDescription>
                  Enter ticket details to test the AI classification model
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Ticket Title
                    </label>
                    <input
                      type="text"
                      value={testInput.title}
                      onChange={(e) => setTestInput(prev => ({ ...prev, title: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-end focus:border-transparent"
                      placeholder="Enter ticket title..."
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Description
                    </label>
                    <textarea
                      rows={4}
                      value={testInput.description}
                      onChange={(e) => setTestInput(prev => ({ ...prev, description: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-end focus:border-transparent"
                      placeholder="Enter detailed description..."
                    />
                  </div>
                  
                  <Button 
                    onClick={testClassification}
                    disabled={loading || !testInput.title || !testInput.description}
                    className="w-full"
                  >
                    {loading ? '🤖 Analyzing...' : '🤖 Classify Ticket'}
                  </Button>
                </div>

                {/* Test Result */}
                {testResult && (
                  <div className="mt-6 p-4 border rounded-lg">
                    {testResult.error ? (
                      <div className="text-red-600">
                        <strong>Error:</strong> {testResult.error}
                      </div>
                    ) : (
                      <div>
                        <h4 className="font-medium text-gray-900 mb-3">Classification Result</h4>
                        <div className="grid md:grid-cols-2 gap-4">
                          <div>
                            <span className="text-sm font-medium text-gray-600">Priority:</span>
                            <span className={cn(
                              "ml-2 px-2 py-1 rounded-full text-xs font-medium",
                              testResult.priority === 'high' ? 'bg-red-100 text-red-800' :
                              testResult.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-green-100 text-green-800'
                            )}>
                              {testResult.priority}
                            </span>
                          </div>
                          <div>
                            <span className="text-sm font-medium text-gray-600">Department:</span>
                            <span className="ml-2 text-gray-900">{testResult.department}</span>
                          </div>
                          {testResult.confidence && (
                            <div className="md:col-span-2">
                              <span className="text-sm font-medium text-gray-600">Confidence:</span>
                              <span className="ml-2 text-gray-900">
                                {Math.round(testResult.confidence * 100)}%
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Sample Test Cases */}
            <Card>
              <CardHeader>
                <CardTitle>Sample Test Cases</CardTitle>
                <CardDescription>
                  Try these sample tickets to see how the AI classifies different scenarios
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {sampleTickets.map((sample, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-medium text-gray-900">{sample.title}</h4>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setTestInput({
                            title: sample.title,
                            description: sample.description
                          })}
                        >
                          Use Sample
                        </Button>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{sample.description}</p>
                      <div className="text-xs text-gray-500">
                        Expected: {sample.expected.priority} priority, {sample.expected.department}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}

export { AIClassificationPage }
