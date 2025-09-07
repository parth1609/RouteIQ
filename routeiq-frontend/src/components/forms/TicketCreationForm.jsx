import React, { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { zammadAPI, zendeskAPI, classifierAPI, handleAPIError } from '@/services/api'
import { cn } from '@/lib/utils'

/**
 * Ticket Creation Form with AI Integration
 * Supports both Zammad and Zendesk with AI-powered classification
 */
const TicketCreationForm = ({ onSuccess, className }) => {
  const [formData, setFormData] = useState({
    platform: 'zammad', // 'zammad' or 'zendesk'
    title: '',
    description: '',
    customerEmail: '',
    customerName: '',
    customerFirstname: '',
    customerLastname: '',
    useAI: true,
  })

  const [aiPrediction, setAiPrediction] = useState(null)
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
    
    // Clear AI prediction when content changes
    if (name === 'title' || name === 'description') {
      setAiPrediction(null)
    }
  }

  const predictClassification = async () => {
    if (!formData.title || !formData.description) {
      setError('Please enter both title and description for AI classification')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await classifierAPI.predict({
        title: formData.title,
        description: formData.description
      })

      setAiPrediction(response.data)
    } catch (err) {
      const errorInfo = handleAPIError(err)
      setError(`AI Classification failed: ${errorInfo.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setError(null)

    try {
      let response
      
      if (formData.platform === 'zammad') {
        const ticketData = {
          title: formData.title,
          description: formData.description,
          customer_email: formData.customerEmail,
          customer_firstname: formData.customerFirstname || formData.customerName.split(' ')[0],
          customer_lastname: formData.customerLastname || formData.customerName.split(' ').slice(1).join(' '),
          use_ai: formData.useAI
        }
        response = await zammadAPI.createTicket(ticketData)
      } else {
        const ticketData = {
          customer_email: formData.customerEmail,
          customer_name: formData.customerName,
          ticket_subject: formData.title,
          ticket_description: formData.description,
          use_ai: formData.useAI
        }
        response = await zendeskAPI.createTicket(ticketData)
      }

      // Reset form
      setFormData({
        platform: 'zammad',
        title: '',
        description: '',
        customerEmail: '',
        customerName: '',
        customerFirstname: '',
        customerLastname: '',
        useAI: true,
      })
      setAiPrediction(null)

      if (onSuccess) {
        onSuccess(response.data)
      }
    } catch (err) {
      const errorInfo = handleAPIError(err)
      setError(`Failed to create ticket: ${errorInfo.message}`)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className={cn("space-y-6", className)}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <span className="text-lg mr-2">🎫</span>
            Create New Ticket
          </CardTitle>
          <CardDescription>
            Create a support ticket with optional AI-powered classification
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Platform Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Platform *
              </label>
              <div className="flex space-x-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="platform"
                    value="zammad"
                    checked={formData.platform === 'zammad'}
                    onChange={handleInputChange}
                    className="mr-2"
                  />
                  <span className="text-sm">Zammad</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="platform"
                    value="zendesk"
                    checked={formData.platform === 'zendesk'}
                    onChange={handleInputChange}
                    className="mr-2"
                  />
                  <span className="text-sm">Zendesk</span>
                </label>
              </div>
            </div>

            {/* Ticket Information */}
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
                Title *
              </label>
              <input
                type="text"
                id="title"
                name="title"
                required
                value={formData.title}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-end focus:border-transparent"
                placeholder="Brief description of the issue"
              />
            </div>

            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                Description *
              </label>
              <textarea
                id="description"
                name="description"
                required
                rows={4}
                value={formData.description}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-end focus:border-transparent"
                placeholder="Detailed description of the issue, steps to reproduce, etc."
              />
            </div>

            {/* Customer Information */}
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="customerEmail" className="block text-sm font-medium text-gray-700 mb-2">
                  Customer Email *
                </label>
                <input
                  type="email"
                  id="customerEmail"
                  name="customerEmail"
                  required
                  value={formData.customerEmail}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-end focus:border-transparent"
                  placeholder="customer@example.com"
                />
              </div>
              
              {formData.platform === 'zammad' ? (
                <>
                  <div>
                    <label htmlFor="customerFirstname" className="block text-sm font-medium text-gray-700 mb-2">
                      First Name
                    </label>
                    <input
                      type="text"
                      id="customerFirstname"
                      name="customerFirstname"
                      value={formData.customerFirstname}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-end focus:border-transparent"
                      placeholder="John"
                    />
                  </div>
                  <div className="md:col-span-1">
                    <label htmlFor="customerLastname" className="block text-sm font-medium text-gray-700 mb-2">
                      Last Name
                    </label>
                    <input
                      type="text"
                      id="customerLastname"
                      name="customerLastname"
                      value={formData.customerLastname}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-end focus:border-transparent"
                      placeholder="Doe"
                    />
                  </div>
                </>
              ) : (
                <div>
                  <label htmlFor="customerName" className="block text-sm font-medium text-gray-700 mb-2">
                    Customer Name
                  </label>
                  <input
                    type="text"
                    id="customerName"
                    name="customerName"
                    value={formData.customerName}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-end focus:border-transparent"
                    placeholder="John Doe"
                  />
                </div>
              )}
            </div>

            {/* AI Classification */}
            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="useAI"
                  checked={formData.useAI}
                  onChange={handleInputChange}
                  className="mr-2"
                />
                <span className="text-sm font-medium text-gray-700">
                  Use AI Classification
                </span>
              </label>
              <p className="text-xs text-gray-500 mt-1">
                Automatically classify priority and department using AI
              </p>
            </div>

            {/* AI Prediction Preview */}
            {formData.useAI && (
              <div className="space-y-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={predictClassification}
                  disabled={loading || !formData.title || !formData.description}
                  className="w-full"
                >
                  {loading ? '🤖 Analyzing...' : '🤖 Preview AI Classification'}
                </Button>

                {aiPrediction && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h4 className="font-medium text-blue-900 mb-2">AI Classification Preview</h4>
                    <div className="grid md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="font-medium text-blue-800">Priority:</span>
                        <span className={`ml-2 px-2 py-1 rounded-full text-xs ${
                          aiPrediction.priority === 'high' ? 'bg-red-100 text-red-800' :
                          aiPrediction.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {aiPrediction.priority}
                        </span>
                      </div>
                      <div>
                        <span className="font-medium text-blue-800">Department:</span>
                        <span className="ml-2 text-blue-700">{aiPrediction.department}</span>
                      </div>
                      {aiPrediction.confidence && (
                        <div className="md:col-span-2">
                          <span className="font-medium text-blue-800">Confidence:</span>
                          <span className="ml-2 text-blue-700">{Math.round(aiPrediction.confidence * 100)}%</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Error Display */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="text-red-800 text-sm">{error}</div>
              </div>
            )}

            {/* Submit Button */}
            <div className="flex space-x-4">
              <Button
                type="submit"
                disabled={submitting}
                className="flex-1"
              >
                {submitting ? 'Creating Ticket...' : 'Create Ticket'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setFormData({
                    platform: 'zammad',
                    title: '',
                    description: '',
                    customerEmail: '',
                    customerName: '',
                    customerFirstname: '',
                    customerLastname: '',
                    useAI: true,
                  })
                  setAiPrediction(null)
                  setError(null)
                }}
              >
                Clear
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

export { TicketCreationForm }
